# Redactions

Every substitution made when packaging these transcripts. Each text pattern
is an exact literal, so no measured value can be altered by accident. The
literals themselves are described rather than printed, so that this log does
not disclose what was withheld.

| What was replaced | Replacement | Occurrences | Reason |
|---|---|---|---|
| a laboratory LAN address | `[LAN-HOST]` | 0 | laboratory control-system host |
| operator home path, escaped form | `[HOME]` | 0 | operator home path |
| operator home path | `[HOME]` | 4 | operator home path |
| operator home path, forward-slash form | `[HOME]` | 2 | operator home path |
| e-mail address on the operator's notebook account | `[ACCOUNT-EMAIL]` | 0 | personal e-mail address |
| session cost in USD, the `total_cost_usd` field | `[COST]` | 25 | no money figure appears in this work |

## The cost redaction

The companion paper's transcript deposit did not redact cost, and its log
carries no such row. The cost is removed here on the author's standing
instruction that no money figure appears in this work. It is removed at the
field level: the `total_cost_usd` value of each session-result record is
replaced, and the per-model usage object that repeats it is dropped whole.
No text was scanned for decimal numbers, because such a scan could touch a
measured quantity. Turns, tool calls, context tokens and wall time, which
are the budget measures the manuscript reports, are kept in full.

## What is not redacted

Specimen identifiers, job ids, segment numbers, server revisions,
chi-squared values, thicknesses, roughnesses, densities and angles are the
provenance this deposit exists to carry. None of them is altered anywhere in
these files.

## Dropped record types

`tool_progress` heartbeats, `rate_limit_event` records, and the `system`
records other than the session-init record (thinking-token counters and hook
start/response notices) carry no scientific content. Per-record uuids,
request ids, thinking-block signatures and the per-model usage object are
removed. The agent's text, reasoning, tool calls and tool results are kept in
full.

Records kept: 10457. Records dropped: 18804.