import pytest
from sparrow_problem_clarifier.core import analyze, SchemaError

def record(**changes):
    return {"id": "one", "description": "MUST: Export CSV\nACCEPT: Rows reconcile", "synthetic": True, "source": "test", **changes}

def test_explicit_extraction_and_evidence():
    spec = analyze([record()])["specs"][0]
    assert spec["requirements"] == [{"text": "Export CSV", "line": 1}]
    assert spec["status"] == "explicit_sections_present"

def test_unstructured_text_is_not_invented():
    spec = analyze([record(description="Make my business efficient")])["specs"][0]
    assert spec["requirements"] == []
    assert len(spec["issues"]) == 2
    assert spec["unresolved_context"]

@pytest.mark.parametrize("changes", [{"amount": -1}, {"amount": 1.5}, {"amount": True}, {"amount": float("nan")}, {"date": "2099-01-01"}, {"date": "bad"}, {"description": "x" * 100001}, {"synthetic": "true"}, {"source": "unknown", "synthetic": False}, {"invented": 1}])
def test_rejects_adversarial_values(changes):
    with pytest.raises(SchemaError):
        analyze([record(**changes)])

def test_duplicate_ids_rejected():
    with pytest.raises(SchemaError, match="duplicate"):
        analyze([record(), record()])

def test_handles_unicode_and_long_inputs():
    text = "MUST: Résumé 東京 😀 C:\\Users\\henry\\data.csv\n" + "context " * 10000
    assert analyze([record(description=text)])["specs"][0]["description"] == text

def test_real_provenance_and_date():
    result = analyze([record(synthetic=False, source="henry-entered", date="2026-09-30", amount=0)])
    assert result["counts"]["real_records"] == 1
