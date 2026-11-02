# Measure translation quality

This is an offline, provider-neutral workflow for comparing English ↔ Tigrinya translations. It makes no paid requests and works without a Gemini key. It does not translate documents by itself.

The starter benchmark contains **150 scenarios across 14 categories**: agreement, negation, aspect, clauses, ambiguity, idioms, everyday messages, school, work, public services, mixed text, quantities, documents, and reverse translation. There are 130 English-source scenarios and 20 Tigrinya-source scenarios. The default profile is Eritrean Tigrinya; a paired document scenario compares general and church spelling without changing the topic.

**These scenarios await native-speaker validation. They are not 150 approved translations.** English scenarios are original test prompts. Reverse scenarios reuse existing repository examples with explicit provenance and provisional glosses. A native reviewer should correct any source problems before the benchmark is used for a release decision. Do not force one exact target string when several natural translations preserve meaning.

## Run a comparison

Commands below run from the repository root. Use Python 3.10 or newer; no packages are required.

```powershell
python scripts/evaluate_translation.py validate
python scripts/evaluate_translation.py prepare --out evaluation/runs/baseline --label baseline --model your-model-name --prompt-version v1
```

Preparation creates a new folder and refuses to overwrite an existing one:

- `manifest.json`: model label, prompt version, selected cases, and benchmark/prompt hashes.
- `requests.jsonl`: one exact prompt per case. Send these prompts to the model or translation workflow you want to evaluate.
- `outputs.jsonl`: fill each record's `translation`, set `status` to `ok`, and optionally record measured `latency_ms` and `cost_usd`. Use `error` for failed requests. Leave unrun cases `pending`. Never label a blank response successful.

Example output record (illustrative only, not a reference translation):

```json
{"id":"reverse-01","status":"ok","translation":"I ate the food.","latency_ms":1250,"cost_usd":null}
```

You can use a different provider or your skill in a fresh conversation. Preserve IDs and record the actual model and instructions used. To compare prompt changes, put the extra instructions in a UTF-8 text file and pass `--instructions path/to/prompt.txt` to `prepare`; the text is saved and hashed. The runner's standard translation instructions are appended. Do not put API keys in instruction files or manifests.

```powershell
python scripts/evaluate_translation.py score --run evaluation/runs/baseline
python scripts/evaluate_translation.py review-template --run evaluation/runs/baseline --out evaluation/runs/baseline/reviews.csv
```

The CSV contains successful candidates, their English/Tigrinya source, context, criteria, and translation hash. Have a fluent reviewer fill the six ratings, `critical_errors`, their reviewer name/ID, and evidence in `notes`; set `status` to `complete`. `corrected_target` is optional. Save as UTF-8 CSV. For two reviewers, duplicate each candidate row with a different reviewer ID; never duplicate the same reviewer/case. Keep reviewer identities consistent across runs. A completed rating is a reviewer judgment, not a verified professional credential.

```powershell
python scripts/evaluate_translation.py score --run evaluation/runs/baseline --reviews evaluation/runs/baseline/reviews.csv
python scripts/evaluate_translation.py prepare --out evaluation/runs/candidate --label candidate --model your-other-model --prompt-version v2
# Generate candidate outputs, then create and fill its review CSV in the same way.
python scripts/evaluate_translation.py score --run evaluation/runs/candidate --reviews evaluation/runs/candidate/reviews.csv
python scripts/evaluate_translation.py compare evaluation/runs/baseline/report.json evaluation/runs/candidate/report.json
```

Each score produces readable `report.md` and detailed `report.json`. Compare uses only cases reviewed in both runs, reports the paired sample size, identifies regressions, and detects newly missing outputs and literal-preservation failures. It rejects different benchmark case sets or scorer versions. Different prompt instructions are allowed and explicitly reported. Rescore both runs after changing the evaluator. Partial coverage is always shown; missing and failed cases stay in the denominator.

## Reviewer rubric

Rate each dimension independently from 0 to 4:

| Rating | Meaning |
| --- | --- |
| 4 | Fully meets the criterion; natural acceptable alternatives are welcome |
| 3 | Minor local issue; useful with a small edit |
| 2 | Substantial correction needed |
| 1 | Mostly fails the criterion |
| 0 | Completely fails or is unusable on this dimension |

| Dimension | Check |
| --- | --- |
| Meaning | Same propositions, negation scope, uncertainty, event order, names, and quantities; no omissions or invented claims |
| Grammar | Agreement, tense/aspect, clauses, object marking, and morphology in the intended variety |
| Naturalness | Idiomatic expression and readable flow rather than word-for-word English phrasing |
| Register | Fits the relationship and audience; familiar/polite forms stay consistent |
| Terminology | Word senses fit context and terms remain consistent; use evidence for specialized vocabulary |
| Style | Follows the selected general/church spelling and formatting preferences; do not turn a valid style variant into a meaning error |

`critical_errors` counts meaning changes that make the output unsuitable: reversed negation, wrong actor/recipient, invented instructions, omitted essential conditions, or changed important quantities. Explain each in `notes`. Do not call a house-spelling preference a critical meaning error. If reviewers differ by two or more points, the report flags disagreement; adjudicate it rather than treating the mean as a final answer. Multiple reviewers are averaged within each case, so heavily reviewed cases do not dominate the overall mean.

There is deliberately no single “accuracy percentage.” No completed human review means **not assessed**. Literal checks only verify exact preservation of identifiers, times, URLs, or quoted labels when the context explicitly requests it. They check occurrence counts too, but cannot prove that a fluent sentence has the right meaning. Legacy checker findings are included as church-style diagnostics, separately from human ratings; they do not grade general Eritrean orthography. Missing latency or cost stays unknown rather than becoming zero. Record timing and cost for failures separately in your provider logs; this report summarizes successful-output measurements only.

## Splits and evidence

Default commands select `dev`. Use development cases to improve prompts and source retrieval. Adjacent related cases share a family, and every family stays in one split. To run the reserved set, put the global option **before** the command:

```powershell
python scripts/evaluate_translation.py --split holdout prepare --out evaluation/runs/holdout-v1 --label holdout-v1 --model your-model --prompt-version v1
python scripts/evaluate_translation.py --split holdout score --run evaluation/runs/holdout-v1
```

Use the same `--split` when preparing, reviewing, and scoring. `--split all` selects both sets. The holdout is public and agent-authored, not a private unseen benchmark. Do not use it as few-shot examples or put its answers into translation memory. Do not improve a prompt on holdout errors and then report the same set as unseen; create a fresh independently reviewed test set for the next release.

No external dataset was downloaded or merged. Candidate external evaluations are [TICO-19](https://tico-19.github.io/testset.html), whose project lists separate Eritrean and Ethiopian Tigrinya, and [FLORES+](https://huggingface.co/datasets/openlanguagedata/flores_plus), whose card specifies evaluation rather than training. Verify the selected data version, access conditions, license, variety, and split before adding it. Keep external results separate from this starter set.

## Improvement loop

1. Validate source scenarios with native Eritrean reviewers; record accepted alternatives and unresolved disagreements. Set a checked case's `review_status` to `reviewed` and add `source_review` containing `reviewer`, `date`, and `notes`. This source approval is separate from ratings of model output. Version every benchmark change.
2. Generate a baseline and review it before changing the model or prompt.
3. Sort failures by category. Fix the largest repeated meaning/grammar problem using sourced grammar or approved translations; change one variable at a time.
4. Repeat on development cases and inspect per-case regressions, not just averages. A style improvement does not compensate for worse meaning.
5. Run the reserved set after selecting a candidate. Use blinded reviewer labels where possible and retain the original responses.
6. Publish sample size, review coverage, critical-error counts, category results, limitations, model/prompt versions, and measured cost/latency. Do not claim native approval for unreviewed material.

Before general release, require complete outputs, complete qualified review of the selected release set, no unresolved critical errors or literal-preservation failures, and adjudication of material disagreement. These are proposed review conditions, not an automatic certification. Do not promote reviewer corrections straight into trusted translation memory without a separate approval decision.

## Developer checks

```powershell
python -m unittest discover -s scripts -p test_evaluation.py -v
python scripts/audit_translation.py --test
```

Run artifacts are ignored by Git because they may contain private translations or reviewer details. Commit deliberately selected, anonymized benchmark changes separately. The workflow does not alter production or install global skills.
