"""Deterministic report rendering with explicit provenance and no savings claims."""
import json

BANNER = "Data provenance: synthetic fixtures are labelled synthetic; real inputs are Henry's own data, entered by him (source: henry-entered)."

def render(result, format="md"):
    if format == "json":
        return json.dumps({"provenance_banner": BANNER, **result}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if format != "md":
        raise ValueError("format: expected md or json")
    lines = ["# Sparrow Problem Clarifier", "", BANNER, "", "Reference date: " + result["as_of"], "", "Counts are computed from supplied records. Section presence does not establish feasibility, completeness, or correctness.", ""]
    lines.extend(f"- {key}: {value}" for key, value in sorted(result["counts"].items()))
    lines += ["", "Savings: unmeasured. No measured baseline supplied; no time or money saved is claimed.", ""]
    for spec in result["specs"]:
        lines += ["## " + spec["id"], "", "Provenance: " + ("synthetic" if spec["synthetic"] else "real, Henry-entered") + "; source: " + spec["source"], "Status: " + spec["status"], "", "Original description:", ""]
        lines.extend("> " + line for line in spec["description"].splitlines())
        for field in ("requirements", "acceptance_criteria", "systems", "pain_points", "unresolved_context"):
            lines += ["", field + ":"]
            lines.extend(f"- Line {entry['line']}: {entry['text']}" for entry in spec[field])
        lines += ["", "Issues: " + (", ".join(spec["issues"]) or "none"), ""]
        lines.extend("- Question: " + question for question in spec["questions"])
        lines.append("")
    return "\n".join(lines) + "\n"
