# Implementation Plan

## Priority 1: Scientific Integrity

- Remove all manual overwrites of experimental metrics.
- Generate Table 2 outputs from evaluated assignments only.
- Keep every synthetic assumption explicitly labeled in outputs and reports.
- Add manuscript reconciliation notes for any value that changes from the current paper/README.

## Priority 2: Data and Reproducibility Foundation

- Replace absolute paths with paths relative to the repository root.
- Add `requirements.txt`, `config.yaml`, and `run_pipeline.py`.
- Move constants such as seed, CRS, zone centers, synthetic capacities, profile loads, and objective weights into config.
- Create an `outputs/` directory tree for metrics, tables, figures, allocations, and reports.

## Priority 3: STGNN

- Implement a real PyTorch GCN-GRU module with deterministic seed support.
- Add a traffic dataset loader that searches for temporal traffic fields.
- If empirical temporal data are absent, stop empirical training with a clear message and optionally run a labeled synthetic experiment.
- Save feature schema, training history, checkpoint, and MAE/RMSE only when a supervised test set exists.

## Priority 4: MILP Correctness

- Keep shared CFE capacity aggregated at substation level.
- Add commute cost to the objective for labor-intensive manufacturing if the manuscript keeps that claim.
- Align Heavy Assembly kVA ranges with the manuscript or document scenario assumptions.
- Apply the same feasibility constraints to comparable MILP baselines.

## Priority 5: Baselines, Ablation, and Sensitivity

- Rename current weighted baseline unless a true AHP pairwise matrix is implemented.
- Add Euclidean MILP, Network MILP, and STGNN-MILP variants with comparable constraints.
- Automate sensitivity runs for -30%, -20%, -10%, 0%, +10%, +20%, +30%.
- Save raw sensitivity runs and aggregate summaries.

## Priority 6: Paper Reconciliation

- Compare generated outputs with the manuscript values.
- Update `MANUSCRIPT_RECONCILIATION.md` whenever the code produces values that differ from the current paper.
- Keep README claims limited to what the code and data actually support.

