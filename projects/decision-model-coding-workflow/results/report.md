# Run report: main-001

Scored 2026-10-02T19:31:32+03:00. Design extra-check-v1, protocol sha256 `ea96874d9b3e918a…`.

## What completed

- Planned cases: 12. Eligible: 12. Ineligible: 0. Catchable (observed residual fault): 1.
- Scheduled selector records: 144. Completed: 144. Invalid: 0.

## Primary comparison (repetition 0, every eligible case)

| Arm | Valid | Coverage match | Caught fault | Missed detectable | Abstentions | Off-reference runs |
|---|---|---|---|---|---|---|
| claude_message | 12/12 | 9/12 | 1/1 | 0/1 | 0 | 3 |
| jev | 12/12 | 12/12 | 1/1 | 0/1 | 0 | 0 |
| winnow_e4b | 12/12 | 12/12 | 1/1 | 0/1 | 0 | 0 |
| filename_rule | 12/12 | 3/12 | 1/1 | 0/1 | 0 | 8 |

Coverage match is agreement with the agent-prepared reference in `oracle/references.json`, not a human label.

## End-to-end time per selector call (all repetitions, valid completed observations)

| Arm | n | Median ms | Range ms |
|---|---|---|---|
| claude_message | 36 | 4063.6 | 2981.2–7953.2 |
| jev | 36 | 414.9 | 329.2–673.2 |
| winnow_e4b | 36 | 1577.6 | 258.8–1783.5 |
| filename_rule | 36 | 0.0 | 0.0–0.0 |

## Selection cost (this run)

| Arm | Calls | Computed USD | Basis |
|---|---|---|---|
| claude_message | 36 | 0.180050 | API-equivalent estimate at published Sonnet 5.5 rates; subscription marginal cash cost not metered |
| jev | 36 | 0.002565 | input tokens x $0.042/M list price, output free |
| winnow_e4b | 36 | 0.000000 | no hosted billing endpoint called; API charge 0 |
| filename_rule | 36 | 0.000000 | local computation; API charge 0 |

Repair attempts: 12, API-equivalent observed 0.321338 USD.

