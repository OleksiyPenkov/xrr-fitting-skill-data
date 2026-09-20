# The tool-server revisions

Section 5.6 of the manuscript names four revisions of the `xrc` tool server, and Table 5
gives the tool surface before and after the changes stage 1 forced. **The server's source
code is not in this deposit, and this file says exactly why and where it is.**

## What the server is

The sessions reached the fitting engine only through `XRC_MCP`, a stdio MCP server that
is one executable of the X-Ray Calc 3 source tree. X-Ray Calc 3 is the software of
references [1] and [3] of the manuscript; it is a separate Delphi codebase with its own
release history, and it is not a product of this study. This study revised its MCP server
component four times while the campaigns ran.

## What is deposited here

| File | What it is |
|---|---|
| `xrc-mcp-server-requirements.md` | The requirements the server was written to, dated 2026-09-08, before any session ran. The tool surface of Table 5 is specified here. |
| `verify-02e7b63.ps1` | The check script for the figure-of-merit defect of 2026-09-12. |
| `verify-06035de.txt`, `verify-2643c4c.txt` | The author's verification logs for the fit-bounds defect of 2026-09-16. |
| `verify-f0168e0.txt`, `verify-7f5b397.txt` | The verification logs for the smoothing revision and for `7f5b397`, the revision rounds 1 and 2 of campaign 1 ran on. |
| `verify-2accc0c-and-dbee34c.txt` | The verification log of `2accc0c` (the five changes of Table 5), the defect it still carried in `report.fringes.contrast`, and the verification of `dbee34c`, which fixed it. This is the log the manuscript means by "The revised server was verified before any session used it". |
| `mcp-config-example.json` | The MCP client configuration one session ran under: the server binary and the per-session working directory. All eighteen session configurations differ only in the working directory. |

## What is not deposited, and where it is

The server source, its unit tests and its own README are in the X-Ray Calc 3 working
repository, which is not part of this deposit. The four revision identifiers the
manuscript cites resolve there. Read from that repository on 2026-09-19, they are:

| Revision | Full hash | Date (UTC+8) | Subject | Files changed |
|---|---|---|---|---|
| `7f5b397` | `7f5b397eed679f8e6765659e80800611da6384f8` | 2026-09-17 14:59:36 | `fit_xrr`: the default population is 500, the lab's practice | 4 files, +71 −7 |
| `2accc0c` | `2accc0cbaff26845f0d411fbe62b7e54b3094e77` | 2026-09-18 22:09:13 | XRC_MCP: `job_wait`, an automatic scale, paired profile parameters and a fit report | 20 files, +12678 −176 |
| `dbee34c` | `dbee34c90c19ab90747ad02d1a84fad375b0b883` | 2026-09-18 22:17:19 | Fit report: the fringe contrast is local, one number per Kiessig fringe | 4 files, +228 −84 |
| `2021a9e` | `2021a9eefdc32e24a3cf24cd390e479afb384787` | 2026-09-19 06:00:26 | `fit_xrr`: `scale_auto`, a boolean spelling of the automatic normalisation | 5 files, +150 −22 |

`2accc0c` also added the change specification `docs/specs/2026-09-18-fit-skill-tool-changes.md`
and the regression tests for the four new capabilities to that repository. The tool
documentation the sessions' clients read is `XRC_MCP/README.md` there, and it differs
between `7f5b397` and `dbee34c`, which is the before-and-after of Table 5.

This table is metadata read from the revision history; it is not the code. Requests for
the server source go to the corresponding author.

## Which revision each session ran on

| Sessions | Revision | Source for the statement |
|---|---|---|
| Campaign 1, stage 1, rounds 1 and 2 | `7f5b397` | Section 5.6; `verify-7f5b397.txt` |
| Campaign 1, stage 1, round 3, and stage 2 | `dbee34c` | Section 5.6; `verify-2accc0c-and-dbee34c.txt` |
| Campaign 2, all twelve transfer sessions | `2021a9e` | Section 5.6; the transfer-test record |

`2accc0c` was never the registered binary: the defect the verification found was fixed in
`dbee34c` eight minutes later, and `dbee34c` is what round 3 ran on.
