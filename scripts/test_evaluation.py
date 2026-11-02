"""Regression tests for truthful coverage, data integrity, and paired comparisons."""
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path

import evaluate_translation as ev


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        scratch = ev.ROOT / "evaluation" / "runs"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        all_cases = ev.load_cases()
        self.cases = [copy.deepcopy(next(c for c in all_cases if c["id"] == key))
                      for key in ("mixed_text-01", "quantities-01", "reverse-01")]
        self.run = self.root / "run"
        ev.prepare(self.cases, self.run, "baseline", "manual-test", "v1")

    def outputs(self, translations, **extras):
        ev.write_jsonl(self.run / "outputs.jsonl", [
            {"id": case["id"], "status": "ok", "translation": text, **extras}
            for case, text in zip(self.cases, translations)])

    def reviews(self, ratings=(4, 4, 4), reviewer="reviewer-a", rows=None):
        path = self.root / "reviews.csv"
        if rows is None:
            ev.review_template(self.cases, self.run, path)
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            for row, rating in zip(rows, ratings):
                row.update({"reviewer": reviewer, "status": "complete", "critical_errors": "0",
                            "notes": "Checked against source and context."})
                row.update({d: str(rating) for d in ev.DIMENSIONS})
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=ev.REVIEW_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        return path, rows

    def test_starter_coverage(self):
        cases = ev.load_cases()
        self.assertEqual(len(cases), 150)
        self.assertEqual(len({c["category"] for c in cases}), 14)
        self.assertEqual({c["direction"] for c in cases}, {"en-ti", "ti-en"})
        self.assertTrue(all(c["review_status"] == "pending_native_review" for c in cases))
        for category in {c["category"] for c in cases}:
            self.assertEqual({c["split"] for c in cases if c["category"] == category}, {"dev", "holdout"})

    def test_duplicate_ids_rejected(self):
        path = self.root / "bad.jsonl"
        ev.write_jsonl(path, [self.cases[0], self.cases[0]])
        with self.assertRaisesRegex(ValueError, "Duplicate case"):
            ev.load_cases(path)

    def test_family_leakage_rejected(self):
        cases = copy.deepcopy(self.cases)
        cases[1]["family"] = cases[0]["family"]
        cases[1]["split"] = "holdout" if cases[0]["split"] == "dev" else "dev"
        path = self.root / "bad.jsonl"
        ev.write_jsonl(path, cases)
        with self.assertRaisesRegex(ValueError, "crosses"):
            ev.load_cases(path)

    def test_benchmark_mutation_rejected(self):
        self.cases[0]["source"] += " changed"
        with self.assertRaisesRegex(ValueError, "Benchmark differs"):
            ev.load_run(self.cases, self.run)

    def test_source_approval_requires_provenance(self):
        cases = copy.deepcopy(self.cases)
        cases[0]["review_status"] = "reviewed"
        path = self.root / "reviewed.jsonl"
        ev.write_jsonl(path, cases)
        with self.assertRaisesRegex(ValueError, "source reviewer"):
            ev.load_cases(path)
        cases[0]["source_review"] = {"reviewer": "editor", "date": "2026-10-29", "notes": "Source/context checked."}
        ev.write_jsonl(path, cases)
        self.assertEqual(ev.load_cases(path)[0]["review_status"], "reviewed")

    def test_requests_mutation_rejected(self):
        requests = ev.read_jsonl(self.run / "requests.jsonl")
        requests[0]["prompt"] += " changed"
        ev.write_jsonl(self.run / "requests.jsonl", requests)
        with self.assertRaisesRegex(ValueError, "changed after"):
            ev.load_run(self.cases, self.run)

    def test_pending_is_not_perfect_quality(self):
        report = ev.score(self.cases, self.run)
        self.assertEqual(report["summary"]["successful"], 0)
        self.assertEqual(report["summary"]["missing_or_failed"], 3)
        self.assertIsNone(report["summary"]["human_mean_0_to_4"]["meaning"])
        self.assertIn("Not assessed", ev.markdown_report(report))

    def test_no_reviews_does_not_invent_semantic_grade(self):
        self.outputs(["help@example.org", "09:30", "Wrong meaning"])
        report = ev.score(self.cases, self.run)
        self.assertEqual(report["summary"]["successful"], 3)
        self.assertEqual(report["summary"]["literal_failed_cases"], 0)
        self.assertIsNone(report["summary"]["human_mean_0_to_4"]["meaning"])
        self.assertIsNone(report["cases"][2]["legacy_diagnostics"])

    def test_literal_loss_and_duplicate_detected(self):
        self.outputs(["help@example.org help@example.org", "10:30", "I ate the food."])
        report = ev.score(self.cases, self.run)
        self.assertEqual(report["summary"]["literal_failed_cases"], 2)

    def test_unicode_literal_preserved(self):
        case = copy.deepcopy(self.cases[0])
        case.update(source="Hello 😊.", required_literals=["😊"])
        run = self.root / "unicode"
        ev.prepare([case], run, "emoji", "test", "v1")
        ev.write_jsonl(run / "outputs.jsonl", [{"id": case["id"], "status": "ok", "translation": "ሰላም 😊።"}])
        self.assertEqual(ev.score([case], run)["summary"]["literal_failed_cases"], 0)

    def test_literal_substrings_are_not_preserved_identifiers(self):
        for text, literal in (("12.5", "2.5"), ("109:30", "09:30"),
                              ("help@example.org.evil", "help@example.org"),
                              ("https://example.org/help/extra", "https://example.org/help")):
            self.assertEqual(ev.literal_count(text, literal), 0)
        self.assertEqual(ev.literal_count("Contact help@example.org.", "help@example.org"), 1)

    def test_empty_success_rejected(self):
        self.outputs(["", "09:30", "text"])
        with self.assertRaisesRegex(ValueError, "empty"):
            ev.load_run(self.cases, self.run)

    def test_duplicate_unknown_and_nonstring_ids_rejected(self):
        for key in (self.cases[0]["id"], "unknown", ["invalid"]):
            ev.write_jsonl(self.run / "outputs.jsonl", [
                {"id": self.cases[0]["id"], "status": "ok", "translation": "text"},
                {"id": key, "status": "ok", "translation": "text"}])
            with self.assertRaisesRegex(ValueError, "Unknown or duplicate"):
                ev.load_run(self.cases, self.run)

    def test_missing_outputs_count_in_denominator(self):
        self.outputs(["help@example.org"])
        result = ev.score(self.cases, self.run)["summary"]
        self.assertEqual(result["cases"], 3)
        self.assertEqual(result["missing_or_failed"], 2)

    def test_invalid_metrics_rejected(self):
        for value in (-1, True, float("nan"), "fast"):
            self.outputs(["text"], latency_ms=value)
            with self.assertRaisesRegex(ValueError, "invalid latency"):
                ev.load_run(self.cases, self.run)

    def test_reviews_require_matching_translation_hash(self):
        self.outputs(["help@example.org", "09:30", "I ate the food."])
        path, _ = self.reviews()
        self.outputs(["changed", "09:30", "I ate the food."])
        with self.assertRaisesRegex(ValueError, "stale output"):
            ev.score(self.cases, self.run, path)

    def test_incomplete_reviews_do_not_count(self):
        self.outputs(["help@example.org", "09:30", "I ate the food."])
        path = self.root / "pending.csv"
        ev.review_template(self.cases, self.run, path)
        self.assertEqual(ev.score(self.cases, self.run, path)["summary"]["human_reviewed"], 0)

    def test_review_identity_and_ranges_required(self):
        self.outputs(["help@example.org", "09:30", "I ate the food."])
        _, rows = self.reviews()
        for field, value in (("meaning", "5"), ("meaning", ""), ("critical_errors", "-1"),
                             ("reviewer", ""), ("notes", "")):
            changed = copy.deepcopy(rows)
            changed[0][field] = value
            path, _ = self.reviews(rows=changed)
            with self.assertRaises(ValueError):
                ev.score(self.cases, self.run, path)

    def test_multiple_reviewers_weight_cases_equally_and_flag_disagreement(self):
        self.outputs(["help@example.org", "09:30", "I ate the food."])
        _, rows = self.reviews()
        second = copy.deepcopy(rows[0])
        second.update(reviewer="reviewer-b", meaning="0", critical_errors="1")
        path, _ = self.reviews(rows=rows + [second])
        s = ev.score(self.cases, self.run, path)["summary"]
        self.assertEqual(s["human_reviewed"], 3)
        self.assertEqual(s["human_mean_0_to_4"]["meaning"], 3.333)
        self.assertEqual(s["critical_error_cases"], 1)
        self.assertEqual(s["reviewer_disagreement_cases"], 1)

    def test_duplicate_reviewer_case_rejected(self):
        self.outputs(["help@example.org", "09:30", "I ate the food."])
        _, rows = self.reviews()
        path, _ = self.reviews(rows=rows + [rows[0]])
        with self.assertRaisesRegex(ValueError, "unique"):
            ev.score(self.cases, self.run, path)

    def test_review_template_contains_source_context_and_candidate(self):
        self.outputs(["help@example.org"])
        _, rows = self.reviews(ratings=(4,))
        self.assertEqual(rows[0]["source"], self.cases[0]["source"])
        self.assertEqual(rows[0]["translation"], "help@example.org")
        self.assertTrue(rows[0]["criteria"])

    def test_comparison_uses_paired_reviews_and_reports_regressions(self):
        self.outputs(["help@example.org", "09:30", "I ate the food."])
        path, _ = self.reviews()
        before = ev.score(self.cases, self.run, path)
        after = copy.deepcopy(before)
        after["cases"][0]["human_ratings"]["meaning"] = 2
        after["cases"][1]["human_ratings"] = None
        result = ev.compare_reports(before, after)
        self.assertEqual(result["paired_human_reviewed_cases"], 2)
        self.assertEqual(result["human_delta_0_to_4"]["meaning"], -1)
        self.assertEqual(result["regressions"][0]["id"], self.cases[0]["id"])

    def test_comparison_rejects_different_benchmark_or_scorer(self):
        before = ev.score(self.cases, self.run)
        for where, key in (("manifest", "benchmark_sha256"), (None, "scorer_sha256")):
            after = copy.deepcopy(before)
            (after[where] if where else after)[key] = "changed"
            with self.assertRaisesRegex(ValueError, "Cannot compare"):
                ev.compare_reports(before, after)

    def test_different_prompt_instructions_supported(self):
        other = self.root / "new-prompt"
        ev.prepare(self.cases, other, "new", "test", "v2", "Use concise natural prose.")
        before = ev.score(self.cases, self.run)
        after = ev.score(self.cases, other)
        result = ev.compare_reports(before, after)
        self.assertTrue(result["prompt_changed"])
        self.assertIsNone(result["human_delta_0_to_4"]["meaning"])


if __name__ == "__main__":
    unittest.main()
