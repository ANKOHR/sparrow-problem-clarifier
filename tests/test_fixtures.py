import json
from sparrow_problem_clarifier.fixtures import generate, fixture_records, expectations
from sparrow_problem_clarifier.core import analyze

def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    assert (tmp_path / "records.jsonl").read_text().startswith("# SYNTHETIC")
    assert all(r["synthetic"] is True for r in fixture_records())
    assert json.loads((tmp_path / "expectations.json").read_text())["synthetic"] is True

def test_fixture_ground_truth_matches_hand_computed():
    assert analyze(fixture_records())["counts"] == expectations()["counts"]

def test_corruption_changes_computed_figures():
    records = fixture_records()
    records[0]["description"] = "Unstructured client request"
    result = analyze(records)
    assert result["counts"]["explicit_sections_present"] == 49
    assert result["counts"]["missing_requirements"] == 101
    assert expectations()["counts"]["explicit_sections_present"] == 50
