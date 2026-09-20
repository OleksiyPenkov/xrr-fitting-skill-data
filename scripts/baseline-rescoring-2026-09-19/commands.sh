#!/bin/sh
# Re-scoring of the CoC4 (P2-04) and CoC5 (P2-05) fits on one footing, 2026-09-19.
# Copies of the record's scripts live in this directory; the only edit is the output path
# (./out/author-grid-score-<job>.json instead of writing into the record's job folder).
REC=D:/MultilayerLab/Papers/LLM-XRay-Optics-Lab/experiments
WD=$REC/runs/exp-03/workdir
REF4=$REC/runs/exp-03/author-reference/author-fit-P2-04-full-fit.xrcx
REF5=$REC/runs/exp-03/author-reference/author-fit-P2-05-Manual-2026-09-18.xrcx

# missing rows (baselines, and CoC5 stage-2 which had no stored score)
python score_on_author_grid.py "$WD" fit-20260917-134808-b160 "$REF4"
python score_on_author_grid.py "$WD" fit-20260917-160911-e2fe "$REF4"
python score_on_author_grid.py "$WD" fit-20260918-144637-1bcc "$REF5"
python score_on_author_grid.py "$WD" fit-20260918-234800-7b64 "$REF5"

# reproducibility check against the three stored author-grid-score.json files
python score_on_author_grid.py "$WD" fit-20260918-233743-691e "$REF4"
python score_on_author_grid.py "$REC/skill-dev-2026-09-18/workdir-T04c" fit-20260918-222358-b830 "$REF4"
python score_on_author_grid.py "$REC/skill-dev-2026-09-18/workdir-T05c" fit-20260918-222443-960a "$REF5"
