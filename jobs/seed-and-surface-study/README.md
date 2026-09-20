# The seed and surface-layer study of Section 7.5

Eight fits of CoC4, testing whether the roughness assignment within a period is decided by the data or by
the optimizer's seed, and whether a light surface layer accounts for the residual mismatch.

Two axes. `no-layer` and `with-layer` are the starting model, without and with a carbon layer on top of the
stack. `start-expert-sigma` and `start-agent-sigma` are the starting roughness assignment: the expert's
pair, sigma_C 5.6 and sigma_Co 2.5 angstroms, or the agent's, sigma_C 2.6 and sigma_Co 4.3. `seed-1` and
`seed-2` are two further seeds from the agent's start.

| Directory | Start sigma_C / sigma_Co (A) | Seed | chi2 | Table 6 row |
|---|---|---|---|---|
| `CoC4-no-layer-start-expert-sigma` | 5.6 / 2.5 | 20260918 | 7.9401 | The agent's, without layer |
| `CoC4-no-layer-start-agent-sigma` | 2.6 / 4.3 | 20260918 | 7.9401 | The agent's, without layer |
| `CoC4-no-layer-seed-1` | 2.6 / 4.3 | 1 | 7.1263 | Seed 1, without layer |
| `CoC4-no-layer-seed-2` | 2.6 / 4.3 | 2 | 7.12631 | Seed 2, without layer |
| `CoC4-with-layer-start-expert-sigma` | 5.6 / 2.5 | 20260918 | 6.09078 | The agent's, with layer |
| `CoC4-with-layer-start-agent-sigma` | 2.6 / 4.3 | 20260918 | 6.09078 | The agent's, with layer |
| `CoC4-with-layer-seed-1` | 2.6 / 4.3 | 1 | 6.22626 | Seed 1, with layer |
| `CoC4-with-layer-seed-2` | 2.6 / 4.3 | 2 | 6.09108 | Seed 2, with layer |

**The result the section rests on is in the first two rows.** Two fits started from opposite roughness
assignments, one the expert's and one the agent's, return the same chi2 to every digit recorded, 7.9401.
The starting assignment does not survive the fit, because the swarm is seeded over the whole bound range.
The same holds with the surface layer, at 6.09078.

These directories were renamed for this deposit. In the laboratory record they carry an A and B scheme in
which A is the layer axis and the words `periodic` and `surface` mark the two starting assignments, which
reads backwards. The job ids are unchanged and are the link to the record.
