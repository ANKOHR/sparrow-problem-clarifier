from sparrow_problem_clarifier.core import analyze
from sparrow_problem_clarifier.fixtures import fixture_records, expectations
from sparrow_problem_clarifier.report import render
import json

def test_report_matches_ground_truth_exact():
    report = json.loads(render(analyze(fixture_records()), "json"))
    assert report["counts"] == expectations()["counts"]

def test_report_zero_false_positives():
    result = analyze(fixture_records())
    for issue, ids in expectations()["issue_ids"].items():
        assert [s["id"] for s in result["specs"] if issue in s["issues"]] == ids

def test_report_carries_provenance_banner():
    for format in ("md", "json"):
        assert "Data provenance:" in render(analyze([]), format)

def test_hypothetical_figures_labelled():
    result = analyze([])
    assert result["savings"]["status"] == "unmeasured"
    assert result["savings"]["time_saved"] is None
    assert result["savings"]["money_saved"] is None
    assert "unmeasured" in render(result)

def test_determinism_byte_identical():
    for format in ("md", "json"):
        assert render(analyze(fixture_records()), format).encode() == render(analyze(fixture_records()), format).encode()

def test_no_em_dashes_in_outputs():
    for format in ("md", "json"):
        assert chr(0x2014) not in render(analyze(fixture_records()), format)
