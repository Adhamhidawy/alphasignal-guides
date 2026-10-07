# next-check: one decision call after Claude Code's required checks

`next_check.py` adds one closed question to a Claude Code workflow. After Claude Code edits the code and your required checks pass, it asks a decision model **which ONE extra check should run**: targeted tests, integration tests, a security suite, or `inspect_first` when the evidence is too thin to choose. Required checks always run. The answer can only add one check from your allowlist, and nothing the model returns is executed.

It speaks the TypeSafe `/v1/systemone` request shape, so the same code calls hosted Jev or a local model served by [Ollaya](https://ollaya.dev). This folder also holds the rename bug from my test, so you can reproduce the example before you point the wrapper at your own repository.

This is the companion to my AlphaSignal article on [adding a decision model to your coding workflow](https://alphasignal.ai/news/how-to-add-a-decision-model-to-your-coding-workflow). The interactive [Decision Model Field Guide](https://adhamhidawy.github.io/alphasignal-guides/projects/decision-model-coding-workflow/) goes with it: where decision calls go in the loop, which model fits your setup, the code for Jev, Ollaya, Perplexity, and Cloudflare, and all 144 answers from my test. `index.html` in this folder is that same page.

## What's in this folder

| Path | What it is |
|---|---|
| `index.html` | The Decision Model Field Guide, one self-contained page |
| `next_check.py` | The wrapper: Claude Code, then your required checks, then one decision call |
| `replay_packet.py` | Sends one of the 12 scored packets to a model again |
| `cases/rename/` | The small document API with the rename bug, its config, and its tests |
| `cases/rename-claude-fix.diff` | The one-line fix Claude Code made in my test |
| `packets/` | The exact request each picker got for the 12 fixes in the scored run |
| `results/` | All 144 scored answers from that run, with a guide to the fields |
| `scripts/` | Builds the demo repository and runs Ollaya inside this folder |
| `tests/` | 13 offline tests |

## Get the code

The project lives inside the alphasignal-guides repository, so clone that and work from this folder:

```bash
git clone --depth 1 https://github.com/Adhamhidawy/alphasignal-guides.git
```

```bash
cd alphasignal-guides/projects/decision-model-coding-workflow
```

Every command below runs from here.

## What it does, in order

1. **Claude Code** (optional, skipped with `--no-agent`) runs headless on the task with the tools and paths you allow.
2. **Required checks** from `next_check.toml` run. If one fails, the wrapper stops before any decision call and exits 2.
3. **The packet** is built from git and your config: the task, an optional contract file, changed paths, line counts, the diff (capped), the required-check results, and your extra suites with their descriptions and test names.
4. **One decision call** goes to `POST {base_url}/v1/systemone` with `model`, `state`, and one `next_check` Choice question.
5. **The log** in `.next-check/runs.jsonl` records the choice, the probabilities, the confidence, the usage, and the time. It also records what a simple filename rule would have picked. The exact packet goes in `.next-check/packets/`.
6. **Shadow mode** (the default) stops there. `--run-extra` runs the one allowlisted command mapped to the choice and exits 1 if it fails. If the pick is `inspect_first`, or the confidence is under `--min-confidence`, nothing runs and the wrapper asks for a person.

## Setup

I tested it on an Apple silicon Mac (macOS 26.5.2, 24 GiB) with Python 3.12 through `uv`, git, and Claude Code 2.1.287.

```bash
uv sync --locked
```

### Local decision model (Ollaya and winnow:e4b)

Download the installer, read it, then install into this folder with no background service. Everything Ollaya writes stays under `.ollaya/`.

```bash
curl -sS --proto '=https' --tlsv1.2 -L -o ollaya-install.sh https://ollaya.dev/install.sh
```

```bash
OLLAYA_INSTALL_DIR="$PWD/.ollaya" OLLAYA_VERSION=0.9.0 OLLAYA_NO_SERVICE=1 OLLAYA_NO_CUDA=1 sh ollaya-install.sh
```

Start the server first, then pull the model (8.0 GB, Q8_0, 8,192-token context). The first decision call loads it, which took about 26 seconds on my Mac.

```bash
nohup scripts/ollaya.sh serve > .ollaya/serve.log 2>&1 &
```

```bash
scripts/ollaya.sh pull winnow:e4b
```

### Hosted Jev (optional)

Store your TypeSafe API key in the macOS Keychain. The prompt hides the input, so the key stays out of your shell history:

```bash
security add-generic-password -a "$USER" -s typesafe-api-key -w
```

Then pass `--backend jev --keychain-service typesafe-api-key`. On other systems, set `TYPESAFE_API_KEY` instead. Either way, the wrapper removes the key from the environment of every command it starts, and never sends it to a local server.

## Reproduce the rename example

`make-rename-repo.sh` creates a small git repository holding the buggy document API. It commits the bug, then applies the one-line fix Claude Code made in my test and leaves it uncommitted:

```bash
scripts/make-rename-repo.sh demo
```

```bash
uv run python next_check.py --repo demo --no-agent
```

What I saw (2026-10-06, warm model):

```text
required  compile_sources: pass (1 passed in 0.01s)
required  public_smoke_suite: pass (7 passed in 0.10s)
required  requested_behavior_regression: pass (1 passed in 0.05s)
decision  winnow:e4b: integration_tests (p=0.6336, confidence=0.5114, 1385.2 ms); filename rule: targeted_tests
shadow mode: logged, not run (python -m pytest tests/extra/test_rename_integration.py)
```

Run the chosen suite:

```bash
uv run python next_check.py --repo demo --no-agent --run-extra
```

```text
extra     integration_tests: fail (1 failed, 3 passed in 0.10s)
```

The failing test is `test_patch_response_matches_the_next_read`. The fix made the rename persist, but the PATCH route still answers with the raw request (`return {**updated, **changes}`). So a padded title comes back padded, while the stored title is trimmed. All 9 required tests pass on this fix.

The same call to Jev:

```bash
uv run python next_check.py --repo demo --no-agent --backend jev --keychain-service typesafe-api-key
```

```text
decision  jev-1.13.0: integration_tests (p=0.87, confidence=0.82, 433.8 ms); filename rule: targeted_tests
```

Your probabilities will differ a little from mine, and from one run to the next. The packet carries each run's test timings, so its bytes change between runs.

### With a live Claude Code run

Start from the bug alone and let the wrapper run Claude Code first. The agent settings are in `cases/rename/next_check.toml`. Claude can edit `./src` only, has no tool that runs commands, and is capped at $0.50. It can still read the rest of the repository, because reads inside the working directory need no approval in `dontAsk` mode.

```bash
scripts/make-rename-repo.sh demo-live --buggy
```

```bash
uv run python next_check.py --repo demo-live --run-extra
```

In my run, Claude Code made the same one-line fix ($0.033 API-equivalent). The required checks passed, winnow:e4b chose `integration_tests`, and that suite failed on the same leftover bug. A live run can produce a different patch, so your result may differ.

## Replay the 12 scored packets

`packets/` holds the exact request every picker received in the scored run, with a table of the reference and each picker's choice. Replaying one locally costs nothing:

```bash
uv run python replay_packet.py packets/I01-k6w753.json --backend local
```

winnow:e4b returns the scored answer for that packet: `integration_tests` at 0.5281 (targeted 0.4284), confidence 0.3708.

## Use it on your repository

1. Copy `cases/rename/next_check.toml` to your repository root.
2. Under `[[required]]`, list the commands your CI already treats as required.
3. Under `[extra.*]`, map each option to a suite you already have. Write the one-sentence description the model reads, and list its test names. Keep `inspect_first` in `[question.criteria]`.
4. Under `[agent]`, widen `files` and the `Read(...)`/`Edit(...)` rules to your layout, and drop `--safe-mode` if you want your CLAUDE.md and hooks loaded. Skip the section and use `--no-agent` if you run Claude Code yourself.
5. Edit `rule_choice()` in `next_check.py` to the rule your team would write by hand.
6. Run in shadow mode on your next 30 to 50 fixes. Then label which extra check mattered and whether it caught anything, and compare the model's choices with the rule's in `.next-check/runs.jsonl`.
7. Add `--run-extra` only if the model misses fewer important checks than the rule, without adding unneeded runs.

The diff is cut at `diff_char_budget` characters (12,000 here). winnow:e4b has an 8,192-token context and caps the state at 6,144 tokens, per Ollaya's model page. The whole rename request used about 1,400.

## Tests

```bash
uv run pytest
```

13 offline tests. They use temporary git repositories, a mocked decision endpoint, and a fake agent, so they make no network or model calls.

## Where these numbers come from

The rename case, its tests, the 12 packets, and the frozen fix come from my extra-check experiment (run `main-001`, 2026-10-02), which an AI coding agent built and ran on my Mac. In that run, Claude Code fixed 12 seeded bugs. Jev, winnow:e4b, Claude in a plain message, and a filename rule then each picked one extra check, three times per fix. That agent also prepared the reference labels, and no person reviewed them. Only the rename fix kept a bug the extra suites could catch, and every picker caught it.

`results/` has all 144 answers, with what each field means, so you can check any number in the article or the guide against the raw records.

## License

The code in this folder is MIT-licensed: see [LICENSE](LICENSE). `index.html` bundles React, Radix UI, cmdk, and the ChatGPT and Claude icons from Lobe Icons, which are MIT-licensed, plus tslib under 0BSD. Their notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
