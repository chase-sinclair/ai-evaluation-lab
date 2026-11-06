import csv
import importlib
import json
from pathlib import Path


def test_sampling_spec_matches_aggregate_frame():
    docs = Path(__file__).resolve().parents[1] / "docs"
    receipt = json.loads((docs / "phase3g_population.json").read_bytes())
    plan = json.loads((docs / "phase3g_sampling_manifest.json").read_bytes())
    assert receipt["source_rows"] - receipt["quarantined"] == receipt["remaining_rows"]
    assert sum(receipt["first_exit_after_quarantine"].values()) == receipt["remaining_rows"]
    assert receipt["additional_cited_review_ids"] == 9
    for stratum in ("positive", "empty"):
        assert plan[stratum]["frame_families"] == receipt["frame"][stratum]["families"]
        assert plan[stratum]["review_ceiling"] <= plan[stratum]["frame_families"]


def test_transitive_exposure_and_unverified_empty_labels(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    mod = importlib.import_module("scripts.audit_crossref_holdout")
    columns = [
        "id",
        "status",
        "relationships",
        "names.types.ror_display",
        "names.types.label",
        "names.types.alias",
        "names.types.acronym",
        "locations.geonames_details.name",
        "locations.geonames_details.country_name",
        "locations.geonames_details.country_subdivision_name",
    ]
    ror = "https://ror.org/"
    path = tmp_path / "registry.csv"
    with path.open("w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, columns)
        writer.writeheader()
        for key, relation, label in [
            ("dev", "child: " + ror + "branch", ""),
            ("branch", "successor: " + ror + "later", ""),
            ("later", "", "fr: Société Exemple"),
            ("independent", "", ""),
            ("other", "", "en: Registered Foundation"),
        ]:
            writer.writerow(
                {
                    "id": ror + key,
                    "status": "active",
                    "relationships": relation,
                    "names.types.ror_display": key,
                    "names.types.label": label,
                    "locations.geonames_details.country_name": "Canada",
                }
            )
    records = [
        ("Prior organisation", "dev"),
        ("Later organisation", "later"),
        ("Societe Exemple Canada", "independent"),
        ("Registered Foundation", ""),
        ("Unknown Foundation", ""),
        ("Unknown Foundation Canada", ""),
        ("Another Organisation", "other"),
    ]
    rows = [
        {"seq_no": i, "input": name, "output": [ror + key] if key else [], "alternates": []}
        for i, (name, key) in enumerate(records)
    ]
    data = mod.screen_population(rows, path, {0}, {ror + "dev"})
    assert data["after_registry_name_screen"] == {"positive": 1, "empty": 3}
    assert data["additional_empty_rows_with_active_name_hit"] == 1
    assert data["frame"]["empty"]["rows"] == 2
    assert data["frame"]["empty"]["families"] == data["frame"]["positive"]["families"] == 1
    assert mod.variants("Example Institute (ABC)", set()) >= {"abc"}
