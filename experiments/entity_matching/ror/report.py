"""Query-level paired replay over the same immutable acquired records."""

from collections import Counter
from time import perf_counter

from scripts.cache_policy_proposal import assess

from ..policies import prediction_ledger
from .core import ABSTAIN, RATES, decision, features, parse


def ratio(n, d):
    return n / d if d else None


def metrics(trials):
    count = Counter()
    for t in trials:
        y, p = t["target"], t["prediction"]
        count["correct"] += p == y
        if y != ABSTAIN:
            count["positive"] += 1
            count["retrieved"] += t["available"]
            count["correct_link"] += y == p
            count["missed_link"] += y != p
            count["incorrect_abstention"] += p == ABSTAIN
        else:
            count["correct_abstention"] += p == ABSTAIN
        count["incorrect_link"] += p != ABSTAIN and p != y
    tp, fp, fn = count["correct_link"], count["incorrect_link"], count["missed_link"]
    return dict(
        n=len(trials),
        **{
            k: count[k]
            for k in (
                "positive",
                "retrieved",
                "correct",
                "correct_link",
                "incorrect_link",
                "missed_link",
                "correct_abstention",
                "incorrect_abstention",
            )
        },
        accuracy=ratio(count["correct"], len(trials)),
        recall_at_5=ratio(count["retrieved"], count["positive"]),
        selection_given_retrieved=ratio(tp, count["retrieved"]),
        precision=ratio(tp, tp + fp),
        recall=ratio(tp, tp + fn),
        f1=ratio(2 * tp, 2 * tp + fp + fn),
    )


def replay(exp, records, thresholds, *, proposal=None, wire_receipts=None):
    cases = {c.id: c for c in exp.load_cases()}
    ledger = prediction_ledger(exp, records, cases)
    proposed = {r["case_id"]: r for r in proposal["requests"]} if proposal else {}
    accounting = {}
    for i, receipt in (wire_receipts or {}).items():
        r = ledger[i]
        expected = proposed[i]
        if (
            r.provider != "openai"
            or r.request_hash != expected["request_sha256"]
            or receipt["run_id"] != r.run_id
        ):
            raise ValueError("Wire receipt does not belong to this acquisition")
        accounting[i] = assess(
            receipt["body"],
            r.response.raw,
            exp.spec.pricing,
            expected["body_sha256"],
            text_only=True,
        )
    start = perf_counter()
    base = {i: decision(c.task_input, thresholds) for i, c in cases.items()}
    ranked = sorted(cases, key=lambda i: (base[i][1], i))
    baseline_ms = (perf_counter() - start) * 1000
    reports = []
    for pct in RATES:
        selected = ranked[: len(ranked) * pct // 100]
        trials = []
        fallbacks = Counter()
        costs = []
        usages = []
        latencies = []
        for i, c in cases.items():
            y = c.ground_truth["resolution"]
            p = base[i][0]
            status = "baseline"
            if i in selected:
                record = ledger.get(i)
                value = parse(record.response, c.task_input) if record else None
                status = record.status if record else "missing_record"
                if status in ("passed", "task_failed") and value is not None:
                    p = value
                else:
                    fallbacks[status] += 1
                costs.append(record.estimated_cost_usd if record else None)
                usages.append(record.response.usage if record else None)
                latencies.append(record.response.latency_ms if record else None)
            top, margin = features(c.task_input)
            trials.append(
                dict(
                    id=i,
                    target=y,
                    baseline=base[i][0],
                    boundary_distance=base[i][1],
                    top_score=top,
                    runner_up_margin=margin,
                    prediction=p,
                    status=status,
                    selected=i in selected,
                    review=c.provenance["review"],
                    group=c.provenance["selection_group"],
                    difficulty="close" if margin < 0.10 else "weak" if top < 0.65 else "clear",
                    available=y in {t["id"] for t in c.task_input["candidates"]},
                )
            )
        cost = None if None in costs else sum(costs)
        policy_costs = [accounting.get(i, {}).get("policy_estimate_usd") for i in selected]
        policy_total = None if None in policy_costs else sum(policy_costs)
        quality = metrics(trials)
        prev = reports[-1] if reports else None
        delta = (
            (cost - prev["usage_estimated_or_mock_usd"])
            if prev and cost is not None and prev["usage_estimated_or_mock_usd"] is not None
            else None
        )
        reports.append(
            dict(
                percent=pct,
                selected_ids=selected,
                fallbacks=dict(fallbacks),
                metrics=quality,
                by_difficulty={
                    g: metrics([t for t in trials if t["difficulty"] == g])
                    for g in ("clear", "weak", "close")
                },
                by_source_group={
                    g: metrics([t for t in trials if t["group"] == g])
                    for g in ("registry_form", "variant", "empty")
                },
                supported_singletons=metrics(
                    [t for t in trials if t["review"] == "source_supported"]
                ),
                introduced=sum(t["baseline"] == t["target"] != t["prediction"] for t in trials),
                repaired=sum(t["baseline"] != t["target"] == t["prediction"] for t in trials),
                measured_provider_usd=None,
                policy_estimated_usd=policy_total,
                usage_estimated_or_mock_usd=cost,
                usage_priced_usd=cost if exp.spec.conditions[0].provider == "openai" else None,
                mock_charge_usd=cost if exp.spec.conditions[0].provider == "mock" else None,
                proposal_reserve_usd=sum(proposed[i]["reserve_usd"] for i in selected)
                if proposed
                else None,
                cache_stop_reasons={
                    i: accounting[i]["stop_reason"]
                    for i in selected
                    if i in accounting and "stop_reason" in accounting[i]
                },
                unknown_cost_rows=costs.count(None),
                known_cost_subtotal=sum(x for x in costs if x is not None),
                marginal_f1_per_usd=(quality["f1"] - prev["metrics"]["f1"]) / delta
                if delta
                and delta > 0
                and quality["f1"] is not None
                and prev["metrics"]["f1"] is not None
                else None,
                input_tokens=None if None in usages else sum(u.input_tokens for u in usages),
                output_tokens=None if None in usages else sum(u.output_tokens for u in usages),
                known_provider_ms=sum(n for n in latencies if n is not None),
                sequential_ms=None if None in latencies else baseline_ms + sum(latencies),
                replay_baseline_ms=baseline_ms,
                trials=trials,
            )
        )
    return reports


def calibrate(rows):
    """Development source-label fit. Maximize correct decisions, then minimize false links."""
    grid = []
    for threshold in (0.45, 0.55, 0.65, 0.75, 0.85):
        for margin in (0.03, 0.08, 0.15):
            correct = wrong_links = 0
            for r in rows:
                y = next(iter(r["output"]), ABSTAIN)
                p, _ = decision(r, (threshold, margin))
                correct += y == p
                wrong_links += p != ABSTAIN and p != y
            grid.append(
                dict(score=threshold, margin=margin, correct=correct, incorrect_links=wrong_links)
            )
    best = max(grid, key=lambda g: (g["correct"], -g["incorrect_links"], g["score"], g["margin"]))
    return dict(
        thresholds=[best["score"], best["margin"]],
        grid=grid,
        training_seq=[r["seq_no"] for r in rows],
    )
