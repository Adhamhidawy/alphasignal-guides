# Results: all 144 scored answers

These files hold every answer from my extra-check test (run `main-001`, scored 2026-10-02). Claude Code fixed 12 bugs that an AI agent seeded into a small document API. `../cases/rename/` holds that API with one of them, the rename bug behind fix I01. For each fix, four pickers chose one extra check, three times each:

- Jev, hosted by TypeSafe
- winnow:e4b, running locally through Ollaya
- Claude in a plain message with no tools
- A rule based on filenames

That's 4 × 12 × 3 = 144 answers. The guide's [Results page](https://adhamhidawy.github.io/alphasignal-guides/projects/decision-model-coding-workflow/#my-results) shows the same data fix by fix.

| File | What it holds |
|---|---|
| `predictions.jsonl` | One JSON line per answer: the pick, the probabilities, the confidence, the time, the cost, and the model that answered |
| `results.csv` | The same 144 answers scored against the reference, one row each, ready for a spreadsheet |
| `references-frozen.json` | The acceptable extra checks for each fix, and the rule used to set them, frozen before the first picker ran |
| `case-index.json` | Maps each case's random ID (`k6w753`) to its fix ID (`I01`) |
| `report.md` | The run's own summary tables, as the test harness wrote them |

## Reading predictions.jsonl

- `arm` is the picker: `jev`, `winnow_e4b`, `claude_message`, or `filename_rule`.
- `case` is the random case ID. `case-index.json` maps it to the fix ID, and the packet files in `../packets/` carry both (`I01-k6w753.json`).
- `repeat` is 0, 1, or 2. Repeat 0 is the primary comparison.
- `choice` is the extra check the picker chose.
- `probabilities`, `p_top`, and `confidence` are what the model returned. Only Jev and winnow:e4b return them. Claude and the rule return a pick only, so these fields are `null` for them.
- `elapsed_ms` is the end-to-end time from my Mac, in milliseconds.
- `computed_estimate_usd` is the cost estimate, and `cost_basis` says how it was worked out. Jev is priced at its list price for input tokens. Claude is an API-equivalent estimate for a run on my subscription. The local model and the rule cost nothing per call.
- `responding_model`, `route`, and `usage` say which model answered, where the request went, and how many tokens it used.

## Reading results.csv

Each row adds the scores to one answer:

- `coverage_match`: the pick is one of the fix's acceptable checks in `references-frozen.json`. `inspect_first` never counts as a match.
- `caught_fault`: the picked suite fails on the fix but passes on the clean code, so it catches a bug the fix left behind.
- `missed_detectable_fault`: the fix left a catchable bug, and the pick doesn't catch it.
- `confirmation`: the picked suite passes on the fix.
- `abstention`: the pick was `inspect_first`.
- `off_reference_run`: the pick is neither an acceptable check nor one that catches a bug, so it would run a suite the reference didn't ask for.

## Two limits

The AI agent that ran the test also wrote the reference checks, and no person reviewed them. It wrote them from the task, the contract, the frozen diff, and the suite descriptions, before any suite ran on the fixes. Only one fix, I01, left a bug an extra suite could catch, and all 12 answers on it caught the bug.

`report.md` points to `oracle/references.json`, a path inside the original test harness, which isn't in this repository. `references-frozen.json` holds the same references, with the SHA-256 of that file.
