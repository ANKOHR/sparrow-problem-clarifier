# Sparrow Problem Clarifier

Sparrow turns explicit statements inside messy client descriptions into traceable technical specs and clarification questions. It is a deterministic Python CLI for small business owners and Sparrow as the vendor. It uses no model, network, GPU, database, or inferred requirements.

## Quickstart

Python 3.10 or later and setuptools are required. From this directory:

```powershell
python -m pip install --no-deps --no-build-isolation -e .
spc fixtures --out demo
spc run --input demo
spc report --format md
python -m pytest -q
```

On Windows, if the user Scripts directory is absent from PATH, add the directory printed by pip to the current shell PATH, or use `python -m sparrow_problem_clarifier.cli` in place of `spc`.

The equivalent shell demo is `spc fixtures --out demo && spc run --input demo && spc report --format md`. It generates 200 synthetic records. For the smallest hand-written five-record version, run `spc run --input examples/tiny` followed by `spc report --format md`.

## Input format reference

Use a directory containing UTF-8 `.json` objects or arrays, or `.jsonl` records. JSONL allows blank lines and whole-line `#` comments. Files and IDs are sorted for deterministic results. All records are processed or the entire run fails; no invalid record is dropped. Only `expectations.json` is reserved fixture metadata and skipped. Subdirectories are not traversed. Other file types, including CSV and YAML, receive a named unsupported-format schema error. This version intentionally supports JSON and JSONL only.

```json
{
  "id": "booking-export",
  "synthetic": true,
  "source": "synthetic-example",
  "description": "Our inbox is chaos.\nPAIN: Copying bookings manually\nSYSTEM: Local CSV\nMUST: Export booking IDs to CSV\nACCEPT: Row count matches the input"
}
```

This example is SYNTHETIC and illustrative, not a trial result. Henry can enter his own real data by setting `synthetic` to `false` and `source` to `henry-entered`. That designation is an input assertion, not identity verification. No real client data is shipped.

Required fields: nonempty string `id` (at most 200 characters), nonempty string `description` (at most 100,000 characters), boolean `synthetic`, and nonempty string `source`. Unknown fields are schema errors. Optional `amount` is an integer in minor currency units between zero and 1,000,000,000,000 inclusive; it is validated but is not a savings estimate or report total. Optional `date` is an ISO YYYY-MM-DD date no later than `--as-of` (default 2026-09-30). The fixed reference date makes validation reproducible; override it explicitly for later real trials. Negative, nonfinite, fractional and boolean amounts are rejected. Duplicate IDs across files fail the entire run. Unicode and Windows paths are retained as supplied; em dashes are rejected, use plain hyphens.

Each nonempty description line with the exact case-sensitive prefix `MUST:`, `ACCEPT:`, `SYSTEM:`, or `PAIN:` supplies a requirement, acceptance criterion, system or pain point respectively. The value must be nonempty. Other lines are preserved as unresolved context. Each extracted statement cites its original description line number. The full original description remains in every spec. The tool does not determine whether an acceptance criterion covers a requirement, whether a request is feasible, or whether it is a complete technical design.

A record lacking MUST statements has `missing_requirements`; lacking ACCEPT statements has `missing_acceptance`. Both present yields `explicit_sections_present`, which is a presence check, not approval. Missing sections and untagged text generate fixed clarification questions. Count denominators are records, not sentences. A record can have both issues, so issue counts can overlap.

## Subcommands

| Command | Purpose | Example |
| --- | --- | --- |
| fixtures | Generate labelled synthetic ground truth | `spc fixtures --out demo` |
| run | Parse, validate, compute and save results | `spc run --input demo --results results.json` |
| report | Recompute saved descriptions and render provenance | `spc report --results results.json --format json --out report.json` |
| spec | Render technical specs without saving results | `spc spec --input examples/tiny` |
| questions | Show clarification questions and per-record provenance | `spc questions --input examples/tiny` |

Every command supports `--help`. Run defaults to `.spc-results.json` in the current working directory; report reads the same path. Reports do not read or compare fixture expectations during normal execution. JSON output includes exact figures, original descriptions and extracted evidence. Markdown includes the same specs and human-readable counts. Named input errors return exit code 2 without tracebacks; argument errors show argparse usage. Malformed JSON names its file and line; schema errors name file, record line and field (JSON array schema errors cite line 1). Missing directories include a usage hint. Output writes use a temporary file and atomic replacement; failures preserve the old target and remove the temporary file. Fixture generation overwrites its two known fixture files.

## Architecture

```text
Local JSON/JSONL -> cli.load -> core.validate -> core.analyze
                                                 |
                                      explicit statements + issues
                                                 |
                                   report.render -> stdout / atomic file
fixtures.generate -> synthetic records + independent expectations
```

Core functions have no I/O. Standard library runtime only. No random generator is used, so no random seed is necessary. Sorting, fixed reference date and no timestamps ensure byte-identical reports for identical input. Runtime timing is recorded separately as machine-specific evidence, not included in deterministic reports.

## Hypothesis and acceptance evidence

Hypothesis: deterministic, explicitly grounded clarification can provide trustworthy section extraction and gap detection. The measurable synthetic outcome is 200 records processed and reported in under five seconds, with every planted issue found and zero false positives. Four groups of 50 give 50 with both sections, 50 missing acceptance, 50 missing requirements, and 50 missing both. Therefore 150 need clarification and each issue occurs 100 times. Independent expectations enumerate all issue IDs. Tests compare exact counts and sets, mutate a planted record, check empty inputs, Unicode, long strings, malformed inputs, schema drift, adversarial amounts and dates, duplicates, atomic write failure, CLI help and repeated output bytes. See EVIDENCE.md for the measured local run.

## Honesty boundary and fixture policy

The tool computes from explicit inputs only. Untagged prose is not promoted to requirements. No predicted accuracy, savings, feasibility, revenue or inferred business value is presented as measured. Time and money saved remain null and labelled unmeasured on CLI and reports; no baseline measurement capability exists in this version. Record counts and issue counts are computed, never illustrative. Synthetic benchmark accuracy measures only the defined section-presence rules, not real-world specification quality.

Every synthetic JSONL file starts with a SYNTHETIC comment and every record has `synthetic: true`. JSON metadata carries both `synthetic: true` and a SYNTHETIC label because JSON cannot contain comments. All reports carry a provenance banner distinguishing synthetic fixtures from Henry-entered real records and include their separate counts. Examples are synthetic too. Local real trial data must not be committed.

## Two-week evidence-based improvement hook

After two weeks of real use, Henry should hand-check a sample of records for incorrect extracted statements or incorrect missing-section flags. Record sample size, errors, error rate (errors / reviewed records), dated run count and whether the tool was used in a private local trial log. Do not ship trial data. If error rate exceeds 10 percent, fix the largest observed failure cause and repeat the sample, or kill with a recorded reason. If never used, kill and record why. Time saved requires measured comparable baseline and tool-run times; no synthetic timing is a savings baseline.

The final verdict is pending the two-week evidence window, not invented by this build. Record a reason and one of: expand for daily use or revenue; integrate for substantial sibling overlap; commercialise if a buyer would pay as-is; maintain for portfolio evidence; kill for no use or unmet acceptance criteria. VERDICT.md holds the current evidence status.

Public publishing is handled by a separate verification step. This build performs local commits only.
