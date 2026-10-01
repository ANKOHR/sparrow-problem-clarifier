import json
import time
import pytest
from sparrow_problem_clarifier.cli import main
from sparrow_problem_clarifier.fixtures import generate

def test_run_completes_on_fixture(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    start = time.perf_counter()
    assert main(["fixtures", "--out", "demo"]) == 0
    assert main(["run", "--input", "demo"]) == 0
    assert main(["report", "--format", "md"]) == 0
    assert time.perf_counter() - start < 5
    assert "Data provenance:" in capsys.readouterr().out

def test_empty_input_renders_without_traceback(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "empty").mkdir()
    assert main(["run", "--input", "empty"]) == 0
    assert main(["report", "--format", "json"]) == 0
    output = capsys.readouterr().out
    assert '"records": 0' in output

@pytest.mark.parametrize("extension,text,line", [("json", '{\n bad', 2), ("jsonl", '# SYNTHETIC\n{bad', 2)])
def test_malformed_input_named_error(tmp_path, capsys, extension, text, line):
    path = tmp_path / ("broken." + extension)
    path.write_text(text)
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "ParseError" in error and path.name in error and f"line {line}" in error

def test_cli_smoke_all_subcommands(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    generate("demo")
    for command in ("run", "spec", "questions"):
        assert main([command, "--input", "demo"]) == 0
    for format in ("md", "json"):
        assert main(["report", "--format", format]) == 0
    for command in ("fixtures", "run", "report", "spec", "questions"):
        with pytest.raises(SystemExit) as error:
            main([command, "--help"])
        assert error.value.code == 0
    assert chr(0x2014) not in capsys.readouterr().out

def test_missing_input_named_error(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "absent")]) == 2
    assert "MissingInput" in capsys.readouterr().err

def test_write_failure_no_partial_files(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    generate("demo")
    assert main(["run", "--input", "demo"]) == 0
    before = set(tmp_path.iterdir())
    assert main(["report", "--out", str(tmp_path)]) == 2
    assert "ReportWriteError" in capsys.readouterr().err
    assert set(tmp_path.iterdir()) == before

def test_schema_error_has_file_line_field(tmp_path, capsys):
    (tmp_path / "bad.jsonl").write_text('# SYNTHETIC\n{"id": "x"}\n')
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "SchemaError" in error and "line 2" in error and "description" in error

def test_cli_bytes_identical(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    generate("demo")
    assert main(["run", "--input", "demo"]) == 0
    assert main(["report", "--out", "first.md"]) == 0
    assert main(["run", "--input", "demo"]) == 0
    assert main(["report", "--out", "second.md"]) == 0
    assert (tmp_path / "first.md").read_bytes() == (tmp_path / "second.md").read_bytes()


def test_report_recomputes_corrupt_cached_totals(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    generate("demo")
    assert main(["run", "--input", "demo"]) == 0
    path = tmp_path / ".spc-results.json"
    cached = json.loads(path.read_text())
    cached["counts"]["records"] = 999
    path.write_text(json.dumps(cached))
    capsys.readouterr()
    assert main(["report", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["counts"]["records"] == 200
