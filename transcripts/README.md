# Agent session transcripts, XRR fitting skill study

The complete sessions behind the manuscript "Teaching a laboratory LLM agent a tacit
procedure: an XRR fitting skill": the baseline agent fits made before the written
procedure existed, the six stage-1 qualification sessions, the agent's own stage-2
session, and the twelve Ru/C transfer sessions. These are the evidence behind Section 6,
Section 7 and Table 7, and behind the session concordance of the Supplementary
Information.

Each directory holds one pair of files per session segment: a `.jsonl` of cleaned
records, one JSON object per line, and a `.md` rendering of the same segment as readable
text. The agent's messages, its reasoning, every tool call it made and every tool result
it received are present in full.

`REDACTIONS.md` lists every substitution made in packaging, with counts.

## Names here are the manuscript's

The manuscript names a session by curve, stage and round, and carries no job id, session
label or segment number in its prose. The directories follow the manuscript. The
laboratory record's own identifiers are given below, and nowhere else in this archive's
file names, so that the run record stays traceable without putting those identifiers back
into the paper's vocabulary.

Specimen concordance, as the Supplementary Information gives it: CoC1 to CoC6 are records
P2-01 to P2-05 and P2-07, C1 is P2-06, and RuC1 to RuC5 and Ru1 are records 260511B,
260908A, 260908B, 260909A, 260910A and 260910B.

## Mapping table

| Directory | Manuscript session | Curve | Laboratory record | Record file | Session id |
|---|---|---|---|---|---|
| `baseline-round-1` | Baseline, round 1 (before the written procedure) | CoC1, CoC2 | exp-03 segment 5 (CoC1) | `stream-segment-5.jsonl` | `bc8f0aa8` |
| `baseline-round-1` | Baseline, round 1 (before the written procedure) | CoC1, CoC2 | exp-03 segment 7 (CoC2) | `stream-segment-7.jsonl` | `bc8f0aa8` |
| `baseline-round-2` | Baseline, round 2 | CoC3, CoC4 | exp-03 segment 9 (CoC3) | `stream-segment-9.jsonl` | `bc8f0aa8` |
| `baseline-round-2` | Baseline, round 2 | CoC3, CoC4 | exp-03 segment 11 (CoC4) | `stream-segment-11.jsonl` | `bc8f0aa8` |
| `baseline-round-3` | Baseline, round 3 | CoC5, C1 | exp-03 segment 14 (CoC5 and C1) | `stream-segment-14.jsonl` | `bc8f0aa8` |
| `stage1-CoC4-round-1` | Campaign 1, stage 1, round 1 | CoC4 | P2-04, session label T04 | `stream-T04.jsonl` | `3751996c` |
| `stage1-CoC4-round-2` | Campaign 1, stage 1, round 2 | CoC4 | P2-04, session label T04b | `stream-T04b.jsonl` | `b76e6622` |
| `stage1-CoC4-round-3` | Campaign 1, stage 1, round 3 | CoC4 | P2-04, session label T04c | `stream-T04c.jsonl` | `8196e6b9` |
| `stage1-CoC5-round-1` | Campaign 1, stage 1, round 1 | CoC5 | P2-05, session label T05 | `stream-T05.jsonl` | `c58ac9b7` |
| `stage1-CoC5-round-2` | Campaign 1, stage 1, round 2 | CoC5 | P2-05, session label T05b | `stream-T05b.jsonl` | `1e5819f1` |
| `stage1-CoC5-round-3` | Campaign 1, stage 1, round 3 | CoC5 | P2-05, session label T05c | `stream-T05c.jsonl` | `2d04b2cd` |
| `stage2-agent` | Campaign 1, stage 2, the agent | CoC4, CoC5 | exp-03 segment 16 (the invalid-JSON fault) | `stream-segment-16.jsonl` | `bc8f0aa8` |
| `stage2-agent` | Campaign 1, stage 2, the agent | CoC4, CoC5 | exp-03 segment 17 (both curves to a verdict) | `stream-segment-17.jsonl` | `bc8f0aa8` |
| `transfer-RuC1-round-a` | Campaign 2, transfer, round a | RuC1 | 260511B, round a | `stream-RuC-260511B-a.jsonl` | `10b150b2` |
| `transfer-RuC1-round-b` | Campaign 2, transfer, round b | RuC1 | 260511B, round b | `stream-RuC-260511B-b.jsonl` | `ce0a8143` |
| `transfer-RuC2-round-a` | Campaign 2, transfer, round a | RuC2 | 260908A, round a | `stream-RuC-260908A-a.jsonl` | `dcfa2dcf` |
| `transfer-RuC2-round-b` | Campaign 2, transfer, round b | RuC2 | 260908A, round b, first launch, stopped by the orchestrator | `stream-RuC-260908A-b-stopped-1106.jsonl` | `7346d25c` |
| `transfer-RuC2-round-b` | Campaign 2, transfer, round b | RuC2 | 260908A, round b, relaunch | `stream-RuC-260908A-b.jsonl` | `21eb455e` |
| `transfer-RuC3-round-a` | Campaign 2, transfer, round a | RuC3 | 260908B, round a | `stream-RuC-260908B-a.jsonl` | `779d8da2` |
| `transfer-RuC3-round-b` | Campaign 2, transfer, round b | RuC3 | 260908B, round b | `stream-RuC-260908B-b.jsonl` | `26b9222f` |
| `transfer-RuC4-round-a` | Campaign 2, transfer, round a | RuC4 | 260909A, round a | `stream-RuC-260909A-a.jsonl` | `9de14acb` |
| `transfer-RuC4-round-b` | Campaign 2, transfer, round b | RuC4 | 260909A, round b | `stream-RuC-260909A-b.jsonl` | `1d83c8f1` |
| `transfer-RuC5-round-a` | Campaign 2, transfer, round a | RuC5 | 260910A, round a | `stream-RuC-260910A-a.jsonl` | `662a8419` |
| `transfer-RuC5-round-b` | Campaign 2, transfer, round b | RuC5 | 260910A, round b | `stream-RuC-260910A-b.jsonl` | `a48b32d1` |
| `transfer-Ru1-round-a` | Campaign 2, transfer, round a | Ru1 | 260910B, round a | `stream-RuC-260910B-a.jsonl` | `29f5a07e` |
| `transfer-Ru1-round-b` | Campaign 2, transfer, round b | Ru1 | 260910B, round b | `stream-RuC-260910B-b.jsonl` | `ccb7113a` |

## Directories do not map one-to-one onto sessions

The baseline and stage-2 directories are segments of a single model session. The agent
was resumed rather than restarted across the whole of the pre-procedure work and the
stage-2 qualification, so one session id, `bc8f0aa8`, covers baseline rounds 1, 2 and 3
and stage 2. The directories split that one session by the manuscript's rounds; the
segment numbers in the file names are the record's own and are those the Supplementary
Information cites. The segments of that session which lie between the rounds, and which
are not fitting work, are not part of this deposit.

Every stage-1 and transfer directory, by contrast, is one fresh session, as Section 5.1
requires: a new session per curve and round, with no memory of any other.

`transfer-RuC2-round-b` holds two files. The first launch of that session was stopped by
the orchestrator shortly after it began, when the task header was amended to lift the
three-fit cap of round a (Section 5.6), and the session was relaunched from the start.
Nothing from the stopped launch was carried forward or used in any result;
`session-stopped.jsonl` is included so that the record is complete, and `session.jsonl`
is the session the manuscript reports.

## What the directories carry

- `baseline-round-1` to `baseline-round-3`: the three rejected rounds of Section 6, before
  any written procedure existed. Round 1 fitted CoC1 and CoC2, round 2 CoC3 and CoC4,
  round 3 CoC5 and the carbon film C1. These are the "before the written procedure" row of
  Table 7.
- `stage1-CoC4-round-*` and `stage1-CoC5-round-*`: the six qualification test sessions of
  Section 7.1 and Table 3, each a fresh session given the written procedure and one curve.
  Rounds 1 and 2 ran on the earlier tool-server revision and round 3 on the revised one,
  which is what Figure 5 and Section 7.4 compare.
- `stage2-agent`: the agent given the same written artifact, Section 7.2. The earlier of
  its two segments is the one in which fourteen fit calls were refused as invalid JSON;
  the later is the session that fitted both curves to a verdict in 13 turns.
- `transfer-RuC1-round-a` to `transfer-Ru1-round-b`: the twelve Ru/C transfer sessions of
  Section 7.3 and Table 4, two per curve, on the material system the procedure was not
  written for.

## What is not here

This archive holds the sessions of the baseline, of both stages of campaign 1, and of
campaign 2. The elicitation session of Section 4, the sensitivity and diagnostic
side-sessions of the skill development, the offline scoring runs of Section 5.7, and the
segments of the baseline session that lie between the rounds are not part of it.

One further pair of segments of the baseline session is not here: the refit of the carbon
film C1 under the amended procedure, reported at the end of Section 7.5 and in the
surface-layer column of Table 6. That refit ran in two parts, the first of which ended on
a laboratory login expiry after its fits had finished, and the second of which read the
results and reported them. The fits themselves are among the job files and fit reports of
the Supplementary Information.
