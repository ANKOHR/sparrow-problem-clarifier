"""Local-only CLI. JSON and comment-labelled JSONL are supported inputs."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import SchemaError, analyze, validate
from .fixtures import generate
from .report import render

class InputError(ValueError):
    pass

def load(directory, as_of="2026-09-30"):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f"MissingInput: {directory}; use --input <existing directory>")
    records = []
    seen = set()
    for path in sorted(directory.iterdir()):
        if path.name == "expectations.json" or path.is_dir():
            continue
        if path.suffix not in (".json", ".jsonl"):
            raise InputError(f"SchemaError: {path}: line 1: unsupported file format; use JSON or JSONL")
        try:
            text = path.read_text(encoding="utf-8-sig")
            if path.suffix == ".jsonl":
                items = []
                for number, line in enumerate(text.splitlines(), 1):
                    if not line.strip() or line.lstrip().startswith("#"):
                        continue
                    try:
                        items.append((number, json.loads(line)))
                    except json.JSONDecodeError as error:
                        raise InputError(f"ParseError: {path}: line {number}: {error.msg}") from None
            else:
                try:
                    value = json.loads(text)
                except json.JSONDecodeError as error:
                    raise InputError(f"ParseError: {path}: line {error.lineno}: {error.msg}") from None
                items = [(1, r) for r in value] if isinstance(value, list) else [(1, value)]
            for number, record in items:
                try:
                    validate(record, as_of)
                    if record["id"] in seen:
                        raise SchemaError("id: duplicate " + record["id"])
                    seen.add(record["id"])
                except SchemaError as error:
                    raise InputError(f"SchemaError: {path}: line {number}: {error}") from None
                records.append(record)
        except UnicodeError as error:
            raise InputError(f"ParseError: {path}: line 1: invalid UTF-8") from error
    return records

def atomic_write(path, content):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    except OSError as error:
        raise InputError(f"ReportWriteError: {path}: {error.strerror}") from None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

def main(argv=None):
    parser = argparse.ArgumentParser(description="Turn explicit client statements into traceable technical specs. No predictions or savings estimates.")
    sub = parser.add_subparsers(dest="command", required=True)
    fixture = sub.add_parser("fixtures", help="Generate 200 labelled synthetic records", epilog="Example: spc fixtures --out demo")
    fixture.add_argument("--out", required=True)
    for command, help_text in (("run", "Compute specs and save results"), ("spec", "Render technical specs directly from inputs"), ("questions", "List clarification questions from missing explicit sections")):
        child = sub.add_parser(command, help=help_text, epilog=f"Example: spc {command} --input demo")
        child.add_argument("--input", required=True)
        child.add_argument("--as-of", default="2026-09-30", help="Fixed reference date for future-date validation, YYYY-MM-DD")
        if command == "run":
            child.add_argument("--results", default=".spc-results.json")
    report = sub.add_parser("report", help="Render saved results with provenance", epilog="Example: spc report --format md")
    report.add_argument("--format", choices=("md", "json"), default="md")
    report.add_argument("--results", default=".spc-results.json")
    report.add_argument("--out", help="Atomic report output file; otherwise stdout")
    args = parser.parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 SYNTHETIC records; expectations are synthetic hand-computed ground truth.")
        elif args.command == "report":
            path = Path(args.results)
            if not path.is_file():
                raise InputError(f"MissingInput: {path}; run spc run --input <dir> first")
            try:
                result = json.loads(path.read_text(encoding="utf-8"))
                # Recompute from original descriptions instead of trusting cached figures.
                records = [{key: s[key] for key in ("id", "description", "synthetic", "source")} for s in result["specs"]]
                result = analyze(records, result["as_of"])
            except (ValueError, KeyError, TypeError) as error:
                raise InputError(f"SchemaError: {path}: line 1: invalid results: {error}") from None
            output = render(result, args.format)
            if args.out:
                atomic_write(args.out, output)
            else:
                print(output, end="")
        else:
            from datetime import date
            try:
                if date.fromisoformat(args.as_of).isoformat() != args.as_of:
                    raise ValueError()
            except ValueError:
                raise InputError("SchemaError: as_of: expected YYYY-MM-DD") from None
            result = analyze(load(args.input, args.as_of), args.as_of)
            if args.command == "run":
                atomic_write(args.results, render(result, "json"))
                print(f"Computed {result['counts']['records']} records. Savings unmeasured. Results: {args.results}")
            elif args.command == "spec":
                print(render(result), end="")
            else:
                print("Clarification questions computed from explicit inputs. Savings unmeasured.")
                for spec in result["specs"]:
                    print(spec["id"] + " [" + ("synthetic" if spec["synthetic"] else "real, Henry-entered") + "]")
                    for question in spec["questions"]:
                        print("- " + question)
        return 0
    except (InputError, SchemaError, OSError) as error:
        print(str(error) if isinstance(error, (InputError, SchemaError)) else f"FileError: {error.filename}: {error.strerror}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
