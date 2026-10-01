"""Pure clarification functions. Savings are unmeasured, never estimated."""
from datetime import date

MAX_DESCRIPTION = 100000
TAGS = {"MUST": "requirements", "ACCEPT": "acceptance_criteria", "SYSTEM": "systems", "PAIN": "pain_points"}
FIELDS = {"id", "description", "synthetic", "source", "date", "amount"}

class SchemaError(ValueError):
    """An explicit input contract violation."""

def validate(record, as_of="2026-09-30"):
    if not isinstance(record, dict):
        raise SchemaError("record: expected object")
    extra = set(record) - FIELDS
    if extra:
        raise SchemaError("unknown field: " + ", ".join(sorted(extra)))
    for field in ("id", "description", "source"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise SchemaError(field + ": expected nonempty string")
    if len(record["id"]) > 200:
        raise SchemaError("id: maximum 200 characters")
    if len(record["description"]) > MAX_DESCRIPTION:
        raise SchemaError("description: maximum 100000 characters")
    if type(record.get("synthetic")) is not bool:
        raise SchemaError("synthetic: expected boolean")
    if not record["synthetic"] and record["source"] != "henry-entered":
        raise SchemaError("source: real records require henry-entered")
    if "amount" in record:
        value = record["amount"]
        if type(value) is not int or value < 0 or value > 10**12:
            raise SchemaError("amount: expected integer minor units from 0 to 1000000000000")
    if "date" in record:
        try:
            value = date.fromisoformat(record["date"])
            if value.isoformat() != record["date"]:
                raise ValueError()
        except (ValueError, TypeError):
            raise SchemaError("date: expected YYYY-MM-DD") from None
        if value > date.fromisoformat(as_of):
            raise SchemaError("date: future date relative to as_of " + as_of)
    if chr(0x2014) in record["description"] or any(chr(0x2014) in str(v) for v in record.values()):
        raise SchemaError("text: em dash is prohibited; use a plain hyphen")
    return record

def clarify(record, as_of="2026-09-30"):
    validate(record, as_of)
    spec = {"id": record["id"], "synthetic": record["synthetic"], "source": record["source"], "description": record["description"]}
    spec.update({key: [] for key in TAGS.values()})
    spec["unresolved_context"] = []
    for number, line in enumerate(record["description"].splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        tag, separator, content = line.partition(":")
        if separator and tag in TAGS and content.strip():
            spec[TAGS[tag]].append({"text": content.strip(), "line": number})
        else:
            spec["unresolved_context"].append({"text": line, "line": number})
    spec["issues"] = []
    if not spec["requirements"]:
        spec["issues"].append("missing_requirements")
    if not spec["acceptance_criteria"]:
        spec["issues"].append("missing_acceptance")
    spec["status"] = "needs_clarification" if spec["issues"] else "explicit_sections_present"
    spec["questions"] = [
        {"missing_requirements": "What exact behavior must the system perform?", "missing_acceptance": "What observable result will confirm acceptance?"}[issue]
        for issue in spec["issues"]
    ]
    if spec["unresolved_context"]:
        spec["questions"].append("Which untagged statements should become explicit requirements or acceptance criteria?")
    return spec

def analyze(records, as_of="2026-09-30"):
    specs, seen = [], set()
    for record in records:
        spec = clarify(record, as_of)
        if spec["id"] in seen:
            raise SchemaError("id: duplicate " + spec["id"])
        seen.add(spec["id"])
        specs.append(spec)
    specs.sort(key=lambda item: item["id"])
    counts = {"records": len(specs), "synthetic_records": sum(s["synthetic"] for s in specs), "real_records": sum(not s["synthetic"] for s in specs), "explicit_sections_present": sum(not s["issues"] for s in specs), "needs_clarification": sum(bool(s["issues"]) for s in specs)}
    for issue in ("missing_requirements", "missing_acceptance"):
        counts[issue] = sum(issue in s["issues"] for s in specs)
    return {"schema_version": 1, "as_of": as_of, "counts": counts, "specs": specs, "savings": {"status": "unmeasured", "time_saved": None, "money_saved": None, "reason": "No measured baseline supplied; savings cannot be reported."}}
