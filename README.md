# Measured reflectivity curves, expert reference fits, fit jobs, the written fitting procedure and the qualification code for a language-model XRR fitting agent

Data and code behind "[CHECK: manuscript title, to be supplied before submission]"
([CHECK: arXiv identifier, to be created before submission]).

The Co/C specimens were deposited in September 2026 on one magnetron sputtering system and
measured on one diffractometer. Every reflectivity curve released here is the instrument's
own scan, as recorded: no refitting, smoothing, interpolation, resampling or background,
footprint or absorption correction was applied to any of them. The expert's reference
projects are the contents of his X-Ray Calc files, unaltered. The fit jobs are the request,
state and report files the tool server wrote, unaltered.

## Version history

- 1.0 ([CHECK: publication date]): the curves, the expert's reference projects, the fit
  jobs, the written procedure, the scripts, the tool-server record and the session
  transcripts.

## Files

| File | Holds |
|---|---|
| `curves/` | The six measured Co/C-campaign curves, each with its instrument metadata and its raw diffractometer scan |
| `fits/` | The expert's withheld reference fits of CoC4 and CoC5, as X-Ray Calc projects and as curve files |
| `jobs/` | The request, state and report files of all 114 fit jobs of both campaigns, by session |
| `procedure/` | The written fitting procedure, and the prompt each of the eighteen test sessions actually received |
| `scripts/` | The qualification scripts, the like-for-like scoring scripts, the figure script and the scripts that built this deposit |
| `server/` | What the laboratory record holds about the four tool-server revisions the manuscript cites |
| `transcripts/` | The complete sessions: messages, reasoning, tool calls and tool results |
| `figures/` | The seven figures of the paper: the two drawn diagrams as SVG and the five plotted figures as PNG |
| `SHA256SUMS.txt` | SHA-256 of every file in this deposit |

## Specimen names

The manuscript names specimens by material system and index. The laboratory record names
them by deposition slot or by the date they were measured. File names in this deposit are
the manuscript's; this table is the mapping, and it is the only place the record's own
names are given.

| Paper name | Record name | What it is | Where it appears in the manuscript |
|---|---|---|---|
| CoC1 | P2-01 | Co/C multilayer | Baseline, first rejected round (§6) |
| CoC2 | P2-02 | Co/C multilayer | Baseline, first rejected round (§6) |
| CoC3 | P2-03 | Co/C multilayer | Baseline, second rejected round (§6) |
| CoC4 | P2-04 | Co/C multilayer | Qualification reference curve 1; the seed study (§7.5) |
| CoC5 | P2-05 | Co/C multilayer | Qualification reference curve 2; baseline third round |
| CoC6 | P2-07 | Co/C multilayer | Deposited on times taken from the rejected fits (§6) |
| C1 | P2-06 | Single carbon film on glass | The elicitation curve (§4); the surface-layer refit (§7.5); the film with no adequate model (§7.6) |
| RuC1 … RuC5, Ru1 | 260511B, 260908A, 260908B, 260909A, 260910A, 260910B | Ru/C multilayers and one Ru film | The transfer test (§7.3) |

Session directory names in `jobs/`, `procedure/` and `transcripts/` are likewise
the manuscript's: curve, stage and round. `jobs/MANIFEST.tsv` carries the record path of
every job folder, so the run record stays traceable.

## What is in this deposit and what is not

**The eight curves of the manuscript.** Section 8.5 states the bounds of the study as "two
material systems, eight curves". Those eight are the two Co/C qualification curves, CoC4
and CoC5, and the six Ru/C curves of the transfer test, RuC1 to RuC5 and the film Ru1.

**Six of those eight are not re-deposited here.** The six Ru/C curves and the expert's fits
of them are the data of the companion paper and are published in its deposit, cited as
reference [42] of the manuscript. They are cited, not copied. What this deposit adds for
them is this study's own product: the forty-two fit jobs the twelve transfer sessions
produced on those curves, in `jobs/` under `campaign2-transfer/`, and the prompts and
transcripts of those sessions.

**Six measured curves are deposited**, all from this study's own Co/C campaign: CoC1 to
CoC5 and the carbon film C1. They include the two of the eight that are this study's, CoC4
and CoC5, and the four further curves of the rejected baseline of Section 6, which are
deposited because Sections 6, 7.5 and 7.6 are argued on them.

**CoC6 has no curve.** CoC6 (record P2-07) was deposited on times taken from the rejected
fits and is discussed in Section 6, but its reflectivity scan never reached the laboratory;
the run record states on 2026-09-18 and again on 2026-09-19 that "P2-07's curve is still
off-site". No measurement of it exists to deposit, and none is fabricated here. Seven Co/C
specimens were made and six were measured.

**The expert's Co/C reference fits are here.** They were withheld from every session while
the study ran, as Section 5.3 states. They are released now, in `fits/`.

## Format of the curve files

`curves/<specimen>.csv` opens with one `#` comment line holding the specimen's paper name,
its record name, the identifier the diffractometer carries for it, the name of the raw scan
file, the specimen's role, and the number of points. Two columns follow:

| Column | Unit | Meaning |
|---|---|---|
| `two_theta_deg` | degree | Scattering angle 2θ |
| `intensity_counts` | counts | Measured intensity at that angle |

The numbers are the tokens of the record's own data file, written out unchanged. Row counts
run from 2891 to 5302. These are counts, not reflectivity: the curves are released as the
instrument recorded them, and the normalization is a step of the fitting procedure, not a
property of the data. `<specimen>.xrdml` is the raw diffractometer scan (PANalytical XRDML)
the CSV was converted from. The instrument software's own text export of each scan exists in
the laboratory record and is not deposited, being a third rendering of the same numbers.

## Format of the instrument metadata files

`curves/<specimen>.meta.json` is the metadata block the laboratory wrote beside each curve
when it was placed in a session's inbox, released as recorded. It carries the wavelength and
its note, the column convention, the scan dates, the instrument description (tube, incident
optic, slits, detector, goniometer radius, stage), the scan parameters (axis, mode, start,
end, step, points, counting time), the detector pulse-height discriminator window, the
sample offsets, the stage position, the name of the raw file, and a `processing` field. That
field reads "none" for every curve in this deposit.

Four of the six scans (CoC3, CoC4, CoC5 and C1) carry `"status_in_file": "Aborted"` with a note explaining it: the
operator stopped the scan once only background was left. The note is the laboratory's, made
at the time, and is reproduced as recorded.

## Format of the fit files

`fits/<name>.xrcx` is an X-Ray Calc project file, exactly as the expert stored it. It is a
zip archive holding the measured curve (`data_<N>.dat`), the curve calculated from the
fitted structure (`calc.dat`), the fitted structure and settings (`params.dsc`) and the
project tree (`project.dsc`). X-Ray Calc is described in references [1] and [3] of the
manuscript.

`fits/<name>.csv` is the contents of that project file, read out by the method of the
companion deposit's `extract_xrr_curves.py` and written in the same three-column form:

| Column | Unit | Meaning |
|---|---|---|
| `two_theta_deg` | degree | Scattering angle 2θ |
| `measured_reflectivity` | dimensionless | Measured reflectivity on that grid, as the project stores it |
| `fitted_reflectivity` | dimensionless | Reflectivity calculated from the fitted structure on the same grid |

The `#` comment line names the project the curve came from and the `min_limit` recorded in
it. The measured and calculated columns share one angular grid within each file.

## Provenance note

`min_limit` is the floor value stored in each project file and is reproduced as recorded. No
claim about the behavior of the fitting program is attached to it.

The reflectivity in the fit files is the expert's own conditioned curve: he normalized and
trimmed it inside X-Ray Calc before fitting. It is therefore not the same object as the
counts in `curves/`, and the two are not interchangeable. Section 5.7 of the manuscript is
about exactly this difference.

## Measured curves (`curves/`)

Six specimens, three files each.

| Specimen | Record | Points | 2θ range (deg) | Step (deg) | Raw scan |
|---|---|---|---|---|---|
| CoC1 | P2-01 | 5302 | 0.09550 – 15.99850 | 0.003 | `XRR 1_Co(260914A).xrdml` |
| CoC2 | P2-02 | 5302 | 0.09550 – 15.99850 | 0.003 | `XRR 1_Co-C(260914B).xrdml` |
| CoC3 | P2-03 | 3585 | 0.10150 – 10.85350 | 0.003 | `XRR-1_Co-C(260916A)-XRR.xrdml` |
| CoC4 | P2-04 | 4899 | 0.10150 – 14.79550 | 0.003 | `XRR-1_Co-C(260916B).xrdml` |
| CoC5 | P2-05 | 4635 | 0.09550 – 13.99750 | 0.003 | `XRR 1_Co-C(260917A).xrdml` |
| C1 | P2-06 | 2891 | 0.09550 – 8.76550 | 0.003 | `XRR 1_C(260917B)-XRR.xrdml` |

Every test session of campaign 1 received the CoC4 or CoC5 curve of this archive: the curve
file in each of the six session working directories of the record is byte-identical to the
record file the CSV here was written from.

## The expert's reference projects (`fits/`)

These are the fits the qualification was measured against. They were withheld from every
session, and the sessions had no file or web access by which to reach them.

| File | Reference for | Stored in the record as |
|---|---|---|
| `CoC4-expert-full-fit.xrcx` | CoC4 | `author-fit-P2-04-full-fit.xrcx` |
| `CoC4-expert-from-agent-project.xrcx` | CoC4 | `author-fit-P2-04-from-agent-project.xrcx` |
| `CoC5-expert.xrcx` | CoC5 | `author-fit-P2-05-Manual-2026-09-18.xrcx` |

**Two different reference fits of CoC4 exist and they are not the same file.** One was made
as a full fit of the curve; the other was made inside the agent's own project file. They
differ in the fitted curve, in the stored measured curve and in the settings: `calc.dat`,
`data_2.dat`, `params.dsc` and `project.dsc` all differ between them. Both are shipped
rather than one being chosen silently. **Every CoC4 number in the manuscript comes from
`CoC4-expert-full-fit.xrcx`**: it is the file the re-scoring of Section 5.7 and Table 7 was
run against (`scripts/baseline-rescoring-2026-09-19/commands.sh` names it as `REF4`) and the
file Figures 4a, 6 and 7 are drawn against (`scripts/make_figures_v3.py`).

There is one reference fit of CoC5. The expert's Ru/C reference fits are not here; they are
in the companion paper's deposit [42].

## Fit jobs (`jobs/`)

One directory per fit job, grouped by campaign and named by the manuscript's session name.
114 fit jobs in all. Each holds the JSON files the tool server wrote:

| File | What it is |
|---|---|
| `request.json` | The fit as the session asked for it: measurement, structure, free parameters, bounds, range, scale, resolution, optimizer settings |
| `job.json` | The job's final state: iterations, best χ², seed, elapsed time, start and finish timestamps |
| `report.json` | The per-fit report: orders, edge, fringes, residual bands and near-bound parameters, for the fit and its start model |
| `author-grid-score.json`, `author-model-score.json` | Where present, the like-for-like χ² of Section 5.7 as it was computed and stored beside that job |

There is no `result.json`: the server writes a fit's result as `report.json` beside
`job.json`. **`report.json` exists for 63 of the 114 jobs and is absent for the rest.** That
is not a gap in the deposit: the per-fit report did not exist in the tool server until
revision `2accc0c`, as Table 5 of the manuscript records, so the jobs of the rejected
baseline and of rounds 1 and 2 of campaign 1 have none. The sessions that ran without it
reconstructed the same quantities by re-querying the server, which is what Section 7.4
counts the cost of.

| Group | Holds |
|---|---|
| `agent-loop/all-fits` | Every fit job of the loop agent's working directory: the three rejected baseline rounds of Section 6, the stage-2 qualification fits of Section 7.2, and the refits under the amended procedure of Section 7.5. One working directory served the agent throughout, and the record does not partition it; the manuscript's named job ids are the last four characters of the directory names |
| `campaign1-stage1/CoC4-round-1 … CoC5-round-3` | The six stage-1 qualification sessions, thirteen fits |
| `campaign1-stage1/aborted-launch-max-turns` | A stage-1 launch that hit the harness turn limit and produced no verdict. It is not one of the six sessions of Table 3 and no result of it is reported in the manuscript; it is here because it ran |
| `campaign2-transfer/RuC1-round-a … Ru1-round-b` | The twelve transfer sessions, forty-two fits: every accepted fit and every discarded profile fit of Table 4 |
| `seed-and-surface-study` | The paired-seed and surface-layer fits of Section 7.5 and Figures 6 and 7 |
| `figure-data` | The measured, calculated and residual curve files of the seven jobs the figure script reads, so that `make_figures_v3.py` can run against this archive. `SOURCE.txt` in each names the job |
| `MANIFEST.tsv` | One row per job: group, session, job id, measurement, state, best χ², start time, elapsed seconds, which files are present, and the job's path in the laboratory record |

Only fit jobs are deposited. The sessions also made 1058 `calc_reflectivity`
jobs, which are the sensitivity maps and order checks the procedure prescribes; they are in
the record and are not here, and the transcripts carry every one of those calls and its
result.

## The written procedure (`procedure/`)

`xrr-fitting-skill.md` is the artifact under test: the laboratory's written procedure for
fitting a measured reflectivity curve, in thirteen sections. **This file is the procedure
verbatim as all twelve transfer sessions of campaign 2 received it** — the procedure text
inside each of the twelve prompts in `as-sent/` is byte-identical to it.

A draft and a sub-draft of the procedure exist in the laboratory record. Neither was given
to any session, and neither is deposited.

`as-sent/<session>.md` is the complete prompt each session received: the task header and the
procedure, concatenated, exactly as sent. These eighteen files are the primary record of
what each session was told, and they are deposited because the procedure changed while the
study ran. Section 5.6 declares the four changes. Their effect is visible here: the
procedure text carried by the six stage-1 prompts falls into three versions, one per round,
and the transfer prompts carry a fourth.

| Prompts | Procedure text | What is new in it |
|---|---|---|
| `stage1-CoC4-round-1.md`, `stage1-CoC5-round-1.md` | Round-1 text | — |
| `stage1-CoC4-round-2.md`, `stage1-CoC5-round-2.md` | Round-2 text | The density bounds, stated explicitly per material, with start values inside them |
| `stage1-CoC4-round-3.md`, `stage1-CoC5-round-3.md` | Round-3 text | Automatic normalization (`scale: "auto"`), paired profile parameters, and the marking of which values are constants of this laboratory |
| the twelve `transfer-*.md` | Identical to `xrr-fitting-skill.md` | A light carbon surface layer in the starting model, the boolean spelling of the automatic scale, and step 9.4, the rule governing when a profile fit may replace a periodic one. The six stage-1 prompts have no 9.4: under them the rule was step 9.3, "keep the fit with the lower chi2" |

The six stage-1 prompts and the six round-a transfer prompts carry the three-fit note of
Section 5.6; the six round-b transfer prompts say instead "as many fits as the procedure
requires".

## Scripts (`scripts/`)

- `make_figures_v3.py` draws the manuscript's Figures 3, 4a, 4b, 5, 6 and 7.
- `qualification/` holds the machinery of the qualification. `run-skilltest.ps1` launches a
  test session against a curve and a procedure file; `make_ruc_skilltest.py` builds the
  twelve transfer working directories from the companion paper's scans;
  `skilltest_compare.py` and `skilltest_compare_ruc.py` check a session's fit against a
  reference fit under the six tolerances of Table 2; `score_author_model.py`,
  `score_on_author_grid.py` and `chi2_offline.py` are the three like-for-like χ²
  comparisons of Section 5.7, with the engine's χ² reproduced offline;
  `overlay_vs_author.py` and the four `p204_*.py` scripts are the record's own figure and
  seed-study scripts the manuscript's figures were adapted from.
- `baseline-rescoring-2026-09-19/` is Section S4 of the Supplementary Information and the
  machinery behind Section 5.7 and Table 7: the scoring scripts, `commands.sh` giving the
  exact invocation for every row of Table 7, and `out/` holding the seven result files those
  commands produced. Its copies of `chi2_offline.py`, `score_author_model.py`,
  `score_on_author_grid.py` and `skilltest_compare.py` are the record's scripts with one
  edit, stated in `commands.sh`: the output path, so that the re-scoring writes into `out/`
  instead of into the record's job folders. The unedited originals are in `qualification/`.
- `build_deposit.py` built this deposit; `build_transcript_deposit.py` built
  `transcripts/`.

Python 3 with numpy and matplotlib; `run-skilltest.ps1` needs PowerShell. **The paths at the
top of each script are the authors' absolute paths into the laboratory record and must be
pointed at this deposit's layout before anything will run.** The scripts that call the
fitting engine also need the `xrc` tool server, which is not in this deposit; see
`server/REVISIONS.md`.

## The tool server (`server/`)

Section 5.6 cites four revisions of the tool server and Table 5 gives its surface before and
after. The server's source is not in this deposit: it is a component of the X-Ray Calc 3
source tree, a separate codebase, not a product of this study. What the laboratory record
holds about those revisions is deposited: the requirements the server was written to, the
verification logs of each revision including the defect one of them still carried, and the
client configuration a session ran under. `REVISIONS.md` lists the four revision
identifiers with their full hashes, dates, subjects and the size of each change as read from
the revision history, says which sessions ran on which revision, and says where the code is.
That file is metadata, not code, and it says so.

## Agent session transcripts (`transcripts/`)

The complete sessions of both campaigns and of the rejected baseline: the model's messages,
its reasoning, every tool call it made and every tool result it received, as cleaned JSONL
and as readable Markdown. Inside the archive, `README.md` explains how the sessions map onto
the manuscript's campaigns, stages and rounds, and `REDACTIONS.md` lists every substitution
made in packaging.

The same substitutions were applied to every text file in the other archives of this
deposit: an operator home path, a laboratory LAN address and a personal e-mail address, each
matched as an exact literal and never as a pattern, so that no measured value can be altered
by accident. No specimen identifier, job id, segment number, server revision, χ², thickness,
roughness, density or angle is redacted anywhere in this deposit.
