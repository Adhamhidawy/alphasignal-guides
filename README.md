# AlphaSignal guides

Interactive guides and runnable code that go with [AlphaSignal](https://alphasignal.ai) articles. GitHub Pages serves every page in this repository, so each guide below opens in your browser with nothing to install.

| Folder | What's inside |
|---|---|
| [`projects/`](projects/) | An article's runnable code together with its interactive guide |
| [`pro-guides/`](pro-guides/) | Guides for AlphaSignal Pro articles |
| [`docs/`](docs/) | Interactive companions, benchmarks, and tools from earlier articles |

## Projects

- [Decision Model Field Guide](https://adhamhidawy.github.io/alphasignal-guides/projects/decision-model-coding-workflow/) ([code](projects/decision-model-coding-workflow/)): add a decision model to a Claude Code loop with `next_check.py`, then check all 144 scored answers from my test.

## Pro guides

- [Qwen 3.8 27B local stack](https://adhamhidawy.github.io/alphasignal-guides/pro-guides/qwen38-27b-local-stack/): an install kit for running Qwen 3.8 27B locally.

## Earlier guides

- [Academic Research Skills](https://adhamhidawy.github.io/alphasignal-guides/docs/academic-research-skills/): the companion to the article on Academic Research Skills, a Claude Code suite with 4 skills and 10 slash commands that turns citation checks into a workflow.
- [agentmemory](https://adhamhidawy.github.io/alphasignal-guides/docs/agentmemory-guide/): architecture, setup, benchmarks, limitations, and a command reference.
- [The Sovereignty Gap](https://adhamhidawy.github.io/alphasignal-guides/docs/bystander-effect-multi-agents/): the bystander effect in multi-agent reasoning. Peer consensus drops a frontier model by up to 88 accuracy points, and the guide shows how to wire around it.
- [Codex App-Server Runtime](https://adhamhidawy.github.io/alphasignal-guides/docs/codex-app-server-runtime/): architecture, setup, use cases, and limits for the opt-in beta in Hermes Agent 2026.5.
- [AlphaSignal Bench](https://adhamhidawy.github.io/alphasignal-guides/docs/kimi-k3-test/): 7 models patch planted bugs in a private full-stack app over 13 tasks and 488 attempts. They're ranked by resolve rate, then by the cost of a working fix.
- KV Cache Debugger, one page per model from the field test: [Fable 5](https://adhamhidawy.github.io/alphasignal-guides/docs/kv-cache-debugger-field-test/fable-5/), [GLM-5.2](https://adhamhidawy.github.io/alphasignal-guides/docs/kv-cache-debugger-field-test/glm-5.2/), [GPT-5.6 Sol (high)](https://adhamhidawy.github.io/alphasignal-guides/docs/kv-cache-debugger-field-test/gpt-5.6-sol-high/), and [Grok 4.5](https://adhamhidawy.github.io/alphasignal-guides/docs/kv-cache-debugger-field-test/grok4.5/). Each one shows KV-cache memory and the attention-score multiplications through prefill and decode.

Built by [Adham Khaled](https://adhamkhaled.vercel.app) for AlphaSignal.
