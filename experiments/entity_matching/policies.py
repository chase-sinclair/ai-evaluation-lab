"""Paired replay of operational policies from a single shared-runner prediction ledger."""

from collections import Counter
from time import perf_counter_ns

from eval_lab.contracts import RunRecord
from eval_lab.core.hashes import digest

from .experiment import THRESHOLD, Experiment, prediction, score, uncertainty


def metrics(pairs: list[tuple[int, int]]) -> dict:
    c = Counter(pairs)
    tn, fp, fn, tp = (c[0, 0], c[0, 1], c[1, 0], c[1, 1])

    def ratio(n, d):
        return n / d if d else None

    return dict(
        n=len(pairs),
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        accuracy=ratio(tp + tn, len(pairs)),
        precision=ratio(tp, tp + fp),
        recall=ratio(tp, tp + fn),
        f1=ratio(2 * tp, 2 * tp + fp + fn),
        fpr=ratio(fp, fp + tn),
        fnr=ratio(fn, fn + tp),
    )


def replay(exp: Experiment, records: list[RunRecord]) -> list[dict]:
    cases = {c.id: c for c in exp.load_cases()}
    condition = exp.spec.conditions[0]
    ledger = {}
    if len({r.run_id for r in records}) > 1:
        raise ValueError("Mixed prediction runs")
    for r in records:
        c = cases.get(r.case_id)
        if (
            not c
            or r.case_id in ledger
            or r.repeat != 0
            or r.condition_id != condition.id
            or (r.dataset_id, r.dataset_version, r.ground_truth)
            != (c.dataset_id, c.dataset_version, c.ground_truth)
            or digest(r.request) != r.request_hash
            or digest(exp.build_request(c, condition)) != r.request_hash
        ):
            raise ValueError("Duplicate or incompatible prediction record")
        ledger[c.id] = r
    start = perf_counter_ns()
    scores = {i: score(c.task_input) for i, c in cases.items()}
    ranked = sorted(cases, key=lambda i: (-uncertainty(scores[i]), i))
    baseline_ms = (perf_counter_ns() - start) / 1e6
    reports = []
    for pct in (0, 25, 50, 100):
        selected = set(ranked[: len(cases) * pct // 100])
        errors = Counter()
        predictions = []
        by_group = {}
        charges = []
        latency = 0.0
        changes = Counter()
        for i, c in cases.items():
            y = c.ground_truth["label"]
            base = int(scores[i] >= THRESHOLD)
            pred = base
            if i in selected:
                r = ledger.get(i)
                if r is None:
                    errors["missing_record"] += 1
                    charges.append(None)
                else:
                    latency += r.response.latency_ms
                    charges.append(r.estimated_cost_usd)
                    value = prediction(r.response)
                    if r.status in ("passed", "task_failed") and value is not None:
                        pred = value
                    else:
                        errors[r.status] += 1
            if pred != base:
                changes["repaired" if pred == y else "introduced"] += 1
            predictions.append((y, pred))
            for g in (c.provenance["group"], str(c.provenance.get("mixture", ""))):
                if g:
                    by_group.setdefault(g, []).append((y, pred))
        cost = sum(charges) if None not in charges else None
        total = metrics(predictions)
        previous = reports[-1] if reports else None
        delta = (
            cost - previous["estimated_api_usd"]
            if previous and cost is not None and previous["estimated_api_usd"] is not None
            else None
        )
        reports.append(
            dict(
                percent=pct,
                selected_ids=[i for i in ranked if i in selected],
                attempted=len(selected) - errors["missing_record"],
                fallbacks=dict(+errors),
                usable=len(selected) - sum(errors.values()),
                repaired=changes["repaired"],
                introduced=changes["introduced"],
                metrics=total,
                by_group={k: metrics(v) for k, v in by_group.items()},
                estimated_api_usd=cost,
                known_api_subtotal_usd=sum(x for x in charges if x is not None),
                incremental_f1_per_usd=(total["f1"] - previous["metrics"]["f1"]) / delta
                if delta
                and delta > 0
                and total["f1"] is not None
                and previous["metrics"]["f1"] is not None
                else None,
                baseline_ms=baseline_ms,
                known_provider_ms=latency,
                estimated_sequential_ms=None if errors["missing_record"] else baseline_ms + latency,
            )
        )
    return reports
