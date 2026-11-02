#!/usr/bin/env python3
"""Offline, provider-neutral translation evaluation. No network calls or AI grading."""
import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASES = ROOT / "evaluation" / "cases.jsonl"
DIMENSIONS = ("meaning", "grammar", "naturalness", "register", "terminology", "style")
REVIEW_FIELDS = ("case_id", "output_sha256", "reviewer", "status", *DIMENSIONS,
                 "critical_errors", "corrected_target", "notes", "source", "translation", "context", "criteria")


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fingerprint(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def literal_count(text, literal):
    """Avoid accepting 2.5 inside 12.5 or an address inside a longer address."""
    left = r"(?<![\w@/+.#=-])" if literal[0].isalnum() else ""
    right = r"(?![\w@/+#=-]|\.[\w]|\?[\w])" if literal[-1].isalnum() else ""
    return len(re.findall(left + re.escape(literal) + right, text))


def read_jsonl(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{number}: expected a JSON object")
        rows.append(row)
    return rows


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def load_cases(path=DEFAULT_CASES):
    cases = read_jsonl(path)
    if not cases:
        raise ValueError("Benchmark is empty")
    ids, families, sources = set(), {}, set()
    for case in cases:
        for field in ("id", "family", "source", "category", "direction", "split", "context", "provenance"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError(f"Case {case.get('id')}: missing/non-string {field}")
        if case["id"] in ids:
            raise ValueError(f"Duplicate case ID: {case['id']}")
        ids.add(case["id"])
        if case["direction"] not in ("en-ti", "ti-en") or case["split"] not in ("dev", "holdout"):
            raise ValueError(f"Case {case['id']}: invalid direction or split")
        if case["family"] in families and families[case["family"]] != case["split"]:
            raise ValueError(f"Case {case['id']}: family crosses dev/holdout boundary")
        families[case["family"]] = case["split"]
        if not isinstance(case.get("profile"), dict) or case["profile"].get("dialect") != "eritrean":
            raise ValueError(f"Case {case['id']}: explicit Eritrean profile required")
        if case["profile"].get("spelling") not in ("general", "church"):
            raise ValueError(f"Case {case['id']}: invalid spelling profile")
        for field in ("criteria", "required_literals", "protected_literals"):
            values = case.get(field)
            if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
                raise ValueError(f"Case {case['id']}: {field} must be a list of nonempty strings")
        if not case["criteria"] or case.get("review_status") not in ("pending_native_review", "reviewed"):
            raise ValueError(f"Case {case['id']}: explicit source review status required")
        if case["review_status"] == "reviewed":
            evidence = case.get("source_review", {})
            if not isinstance(evidence, dict) or any(not isinstance(evidence.get(k), str) or not evidence[k].strip()
                                                      for k in ("reviewer", "date", "notes")):
                raise ValueError(f"Case {case['id']}: source reviewer, date, and notes required")
        for literal in case["required_literals"] + case["protected_literals"]:
            if literal not in case["source"]:
                raise ValueError(f"Case {case['id']}: preservation literal is absent from source")
        key = (case["source"], case["direction"], fingerprint(case["profile"]))
        if key in sources:
            raise ValueError(f"Case {case['id']}: duplicate source/profile")
        sources.add(key)
    return cases


def prompt_for(case, instructions=""):
    target = "Eritrean Tigrinya" if case["direction"] == "en-ti" else "English"
    profile = json.dumps(case["profile"], ensure_ascii=False)
    return ((instructions.strip() + "\n\n" if instructions.strip() else "") +
            f"Translate the source into natural {target}. Preserve its meaning, including negation, "
            f"names, quantities, and uncertainty. Profile: {profile}. "
            "Church spelling, when selected, must not change meaning or add religious content. "
            "Return the translation only; if context leaves an essential ambiguity unresolved, "
            "state that briefly rather than silently inventing a gender or referent. "
            f"Context: {case['context']}\n\nSOURCE:\n{case['source']}")


def prepare(cases, out, label, model, prompt_version, instructions=""):
    if not all(v.strip() for v in (label, model, prompt_version)):
        raise ValueError("Label, model, and prompt version must be nonempty")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "manifest.json", {
        "schema_version": 1, "label": label, "model": model, "prompt_version": prompt_version,
        "created_at": datetime.now(timezone.utc).isoformat(), "benchmark_sha256": fingerprint(cases),
        "case_ids": [c["id"] for c in cases], "case_count": len(cases),
        "instructions": instructions,
        "prompt_sha256": fingerprint([prompt_for(c, instructions) for c in cases]),
        "note": "Unreviewed starter scenarios. This run is not evidence of native-speaker approval.",
    })
    write_jsonl(out / "requests.jsonl", [{"id": c["id"], "prompt": prompt_for(c, instructions)} for c in cases])
    write_jsonl(out / "outputs.jsonl", [{"id": c["id"], "status": "pending", "translation": "",
                                        "latency_ms": None, "cost_usd": None} for c in cases])


def load_run(cases, run):
    run = Path(run)
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("benchmark_sha256") != fingerprint(cases):
        raise ValueError("Benchmark differs from run manifest; use the original cases and split")
    if manifest.get("case_ids") != [c["id"] for c in cases]:
        raise ValueError("Case IDs differ from run manifest")
    instructions = manifest.get("instructions", "")
    if not isinstance(instructions, str):
        raise ValueError("Manifest instructions must be text")
    if manifest.get("prompt_sha256") != fingerprint([prompt_for(c, instructions) for c in cases]):
        raise ValueError("Request prompt version differs from this evaluator")
    expected_requests = [{"id": c["id"], "prompt": prompt_for(c, instructions)} for c in cases]
    if read_jsonl(run / "requests.jsonl") != expected_requests:
        raise ValueError("requests.jsonl was changed after preparation")
    ids = {c["id"] for c in cases}
    outputs = {}
    for row in read_jsonl(run / "outputs.jsonl"):
        case_id = row.get("id")
        if not isinstance(case_id, str) or case_id not in ids or case_id in outputs:
            raise ValueError(f"Unknown or duplicate output ID: {case_id}")
        if row.get("status") not in ("pending", "ok", "error"):
            raise ValueError(f"Output {case_id}: invalid status")
        if not isinstance(row.get("translation"), str):
            raise ValueError(f"Output {case_id}: translation must be a string")
        if row["status"] == "ok" and not row["translation"].strip():
            raise ValueError(f"Output {case_id}: successful translation is empty")
        for field in ("latency_ms", "cost_usd"):
            value = row.get(field)
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                      or not math.isfinite(value) or value < 0):
                raise ValueError(f"Output {case_id}: invalid {field}")
        outputs[case_id] = row
    return manifest, outputs


def review_template(cases, run, path):
    _, outputs = load_run(cases, run)
    with Path(path).open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        for case in cases:
            output = outputs.get(case["id"], {})
            if output.get("status") == "ok":
                writer.writerow({"case_id": case["id"], "output_sha256": digest(output["translation"]),
                                 "status": "pending", "source": case["source"], "translation": output["translation"],
                                 "context": case["context"], "criteria": " / ".join(case["criteria"])})


def load_reviews(path, outputs):
    reviews = defaultdict(list)
    if path is None:
        return reviews
    seen = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(REVIEW_FIELDS).issubset(reader.fieldnames or []):
            raise ValueError("Review CSV is missing required columns")
        for row in reader:
            case_id = row["case_id"]
            output = outputs.get(case_id)
            if output is None or output["status"] != "ok":
                raise ValueError(f"Review {case_id}: no successful output")
            if row["output_sha256"] != digest(output["translation"]):
                raise ValueError(f"Review {case_id}: stale output hash; review the changed translation")
            if row["status"] not in ("pending", "complete"):
                raise ValueError(f"Review {case_id}: invalid status")
            if row["status"] == "pending":
                continue
            reviewer = row["reviewer"].strip()
            if not reviewer or not row["notes"].strip() or (case_id, reviewer) in seen:
                raise ValueError(f"Review {case_id}: reviewer, evidence notes, and unique reviewer/case required")
            seen.add((case_id, reviewer))
            try:
                ratings = {d: int(row[d]) for d in DIMENSIONS}
                critical = int(row["critical_errors"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Review {case_id}: integer ratings and critical error count required") from exc
            if any(v < 0 or v > 4 for v in ratings.values()) or critical < 0:
                raise ValueError(f"Review {case_id}: ratings must be 0–4; critical errors cannot be negative")
            reviews[case_id].append({"reviewer": reviewer, "ratings": ratings, "critical_errors": critical,
                                     "notes": row["notes"], "corrected_target": row["corrected_target"]})
    return reviews


def summarize(rows):
    successful = [r for r in rows if r["status"] == "ok"]
    reviewed = [r for r in successful if r["human_ratings"] is not None]
    checked = [r for r in successful if r["literal_checks"]]
    return {
        "cases": len(rows), "successful": len(successful),
        "missing_or_failed": len(rows) - len(successful), "human_reviewed": len(reviewed),
        "human_review_coverage": round(len(reviewed) / len(rows), 4) if rows else 0,
        "human_mean_0_to_4": {d: round(mean(r["human_ratings"][d] for r in reviewed), 3)
                               if reviewed else None for d in DIMENSIONS},
        "critical_error_cases": sum(r["critical_errors"] > 0 for r in reviewed),
        "reviewer_disagreement_cases": sum(r["reviewer_disagreement"] for r in reviewed),
        "literal_checked_cases": len(checked),
        "literal_failed_cases": sum(any(not c["passed"] for c in r["literal_checks"]) for r in checked),
        "unreviewed_successes": len(successful) - len(reviewed),
        "latency_mean_ms": metric_mean(successful, "latency_ms"),
        "cost_total_usd": sum(r["cost_usd"] for r in successful if r["cost_usd"] is not None)
                          if any(r["cost_usd"] is not None for r in successful) else None,
        "latency_recorded_cases": sum(r["latency_ms"] is not None for r in successful),
        "cost_recorded_cases": sum(r["cost_usd"] is not None for r in successful),
    }


def metric_mean(rows, key):
    values = [r[key] for r in rows if r[key] is not None]
    return round(mean(values), 4) if values else None


def score(cases, run, reviews_path=None):
    manifest, outputs = load_run(cases, run)
    reviews = load_reviews(reviews_path, outputs)
    rows = []
    for case in cases:
        output = outputs.get(case["id"], {"status": "missing", "translation": ""})
        text = output["translation"]
        successful = output["status"] == "ok"
        checks = []
        if successful:
            for field in ("required_literals", "protected_literals"):
                for literal in case[field]:
                    checks.append({"kind": field, "literal": literal,
                                   "passed": literal_count(text, literal) == literal_count(case["source"], literal)})
        human = reviews.get(case["id"], [])
        diagnostic = None
        if successful and case["direction"] == "en-ti":
            from audit_translation import audit_tigrinya
            findings = audit_tigrinya(text)["all_findings"]
            diagnostic = {"findings_by_category": dict(Counter(f["category"] for f in findings)),
                          "rule_ids": [f["rule_id"] for f in findings],
                          "note": "Legacy church-style diagnostics only; not translation accuracy or a general-style grade."}
        rows.append({"id": case["id"], "category": case["category"], "direction": case["direction"],
                     "split": case["split"], "source": case["source"], "context": case["context"],
                     "profile": case["profile"], "criteria": case["criteria"], "translation": text,
                     "status": output["status"], "literal_checks": checks, "legacy_diagnostics": diagnostic,
                     "human_ratings": {d: mean(r["ratings"][d] for r in human) for d in DIMENSIONS} if human else None,
                     "critical_errors": max(r["critical_errors"] for r in human) if human else None,
                     "reviewer_disagreement": any(max(r["ratings"][d] for r in human) - min(r["ratings"][d] for r in human) >= 2
                                                  for d in DIMENSIONS) if human else False,
                     "reviews": human, "latency_ms": output.get("latency_ms"), "cost_usd": output.get("cost_usd")})
    by_category = {k: summarize([r for r in rows if r["category"] == k]) for k in sorted({r["category"] for r in rows})}
    by_direction = {k: summarize([r for r in rows if r["direction"] == k]) for k in sorted({r["direction"] for r in rows})}
    return {"manifest": manifest, "scorer_sha256": digest(Path(__file__).read_text(encoding="utf-8")),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "limitations": ["Starter scenarios await native-speaker validation.",
                            "Literal preservation checks cannot establish semantic correctness.",
                            "Human ratings are supplied by named reviewers; no AI grade is invented.",
                            "Public holdout cases are reserved for testing but are not a private unseen benchmark."],
            "summary": summarize(rows), "by_category": by_category, "by_direction": by_direction,
            "cases": rows}


def markdown_report(report):
    s = report["summary"]
    lines = ["# Translation evaluation", "", f"Run: {report['manifest']['label']}", "",
             f"Completed outputs: {s['successful']}/{s['cases']}; human-reviewed: {s['human_reviewed']}/{s['cases']}.",
             f"Critical-error cases: {s['critical_error_cases']}; literal-preservation failures: {s['literal_failed_cases']}.",
             "", "No human review means quality is **not assessed**, regardless of rule diagnostics.", "",
             "| Dimension | Human mean (0–4) |", "| --- | --- |"]
    lines.extend(f"| {d} | {s['human_mean_0_to_4'][d] if s['human_mean_0_to_4'][d] is not None else 'Not assessed'} |" for d in DIMENSIONS)
    lines.extend(["", "## Coverage", "", "| Category | Outputs | Reviewed | Literal failures |",
                  "| --- | --- | --- | --- |"])
    lines.extend(f"| {k} | {v['successful']}/{v['cases']} | {v['human_reviewed']} | {v['literal_failed_cases']} |" for k, v in report["by_category"].items())
    lines.extend(["", "## Limits", ""] + [f"- {v}" for v in report["limitations"]])
    return "\n".join(lines) + "\n"


def compare_reports(before, after):
    if before.get("scorer_sha256") != after.get("scorer_sha256"):
        raise ValueError("Cannot compare reports made by different scorers; rescore both runs")
    for key in ("benchmark_sha256",):
        if before["manifest"].get(key) != after["manifest"].get(key):
            raise ValueError(f"Cannot compare reports with different {key}")
    left = {r["id"]: r for r in before["cases"]}
    right = {r["id"]: r for r in after["cases"]}
    if left.keys() != right.keys():
        raise ValueError("Cannot compare different case sets")
    paired = [key for key in left if left[key]["human_ratings"] is not None and right[key]["human_ratings"] is not None]
    regressions = []
    for key in paired:
        drops = [d for d in DIMENSIONS if right[key]["human_ratings"][d] < left[key]["human_ratings"][d]]
        if drops or right[key]["critical_errors"] > left[key]["critical_errors"]:
            regressions.append({"id": key, "lower_dimensions": drops,
                                "critical_error_increase": right[key]["critical_errors"] > left[key]["critical_errors"]})
    return {"before": before["manifest"]["label"], "after": after["manifest"]["label"],
            "prompt_changed": before["manifest"]["prompt_sha256"] != after["manifest"]["prompt_sha256"],
            "paired_human_reviewed_cases": len(paired), "total_cases": len(left),
            "human_delta_0_to_4": {d: round(mean(right[k]["human_ratings"][d] - left[k]["human_ratings"][d] for k in paired), 3)
                                   if paired else None for d in DIMENSIONS},
            "regressions": regressions,
            "new_missing_or_failed_ids": [k for k in left if left[k]["status"] == "ok" and right[k]["status"] != "ok"],
            "new_literal_failure_ids": [k for k in left
                                        if left[k]["status"] == "ok" and right[k]["status"] == "ok"
                                        and left[k]["literal_checks"]
                                        and not any(not c["passed"] for c in left[k]["literal_checks"])
                                        and any(not c["passed"] for c in right[k]["literal_checks"])],
            "note": "Paired human reviews only. Ratings are not blinded or statistically significant by default."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--split", choices=("dev", "holdout", "all"), default="dev")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    p = commands.add_parser("prepare")
    for name in ("out", "label", "model", "prompt-version"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--instructions", type=Path, help="Optional prompt instructions to test; saved and hashed with requests")
    p = commands.add_parser("review-template")
    p.add_argument("--run", required=True)
    p.add_argument("--out", required=True)
    p = commands.add_parser("score")
    p.add_argument("--run", required=True)
    p.add_argument("--reviews")
    p = commands.add_parser("compare")
    p.add_argument("before", type=Path)
    p.add_argument("after", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "compare":
            result = compare_reports(json.loads(args.before.read_text(encoding="utf-8")),
                                     json.loads(args.after.read_text(encoding="utf-8")))
        else:
            all_cases = load_cases(args.cases)
            cases = [c for c in all_cases if args.split == "all" or c["split"] == args.split]
            if not cases:
                raise ValueError("Selected split has no cases")
            if args.command == "validate":
                result = {"total": len(all_cases), "selected": len(cases),
                          "categories": dict(Counter(c["category"] for c in cases)),
                          "directions": dict(Counter(c["direction"] for c in cases)),
                          "splits": dict(Counter(c["split"] for c in all_cases))}
            elif args.command == "prepare":
                instructions = args.instructions.read_text(encoding="utf-8") if args.instructions else ""
                prepare(cases, args.out, args.label, args.model, args.prompt_version, instructions)
                result = {"run": args.out, "cases": len(cases), "status": "pending translations"}
            elif args.command == "review-template":
                review_template(cases, args.run, args.out)
                result = {"review_template": args.out}
            else:
                result = score(cases, args.run, args.reviews)
                write_json(Path(args.run) / "report.json", result)
                (Path(args.run) / "report.md").write_text(markdown_report(result), encoding="utf-8")
                result = result["summary"]
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Evaluation error: {exc}\n")


if __name__ == "__main__":
    main()
