"""Synthetic fixtures, no randomness. Counts hand computed: four groups of 50."""
import json
from pathlib import Path

def fixture_records():
    records = []
    for index in range(200):
        group = index // 50
        lines = ["Our booking inbox is a mess. Client context, not an inferred requirement.", "PAIN: Staff copy booking details manually", "SYSTEM: Local booking CSV"]
        if group in (0, 1):
            lines.append("MUST: Export each booking id and date to a local CSV")
        if group in (0, 2):
            lines.append("ACCEPT: Export row count equals the supplied booking count")
        records.append({"id": f"client-{index:03}", "description": "\n".join(lines), "synthetic": True, "source": "synthetic-fixture"})
    return records

def expectations():
    # Independent arithmetic and explicit ranges, never call the engine here.
    return {"synthetic": True, "label": "SYNTHETIC hand-computed ground truth", "counts": {"records": 200, "synthetic_records": 200, "real_records": 0, "explicit_sections_present": 50, "needs_clarification": 150, "missing_requirements": 100, "missing_acceptance": 100}, "issue_ids": {"missing_requirements": [f"client-{i:03}" for i in range(100, 200)], "missing_acceptance": [f"client-{i:03}" for i in list(range(50, 100)) + list(range(150, 200))]}}

def generate(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    records = fixture_records()
    (directory / "records.jsonl").write_text("# SYNTHETIC fixture records\n" + "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    (directory / "expectations.json").write_text(json.dumps(expectations(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
