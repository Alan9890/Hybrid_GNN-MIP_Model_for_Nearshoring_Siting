# Repository Audit

## Current Repository Contents

### Core execution

- `run_pipeline.py`: one-command orchestration for synthetic STGNN preparation/training, GIS simulation, ablation, and sensitivity outputs.
- `simulate_siting.py`: GIS loading, road-graph construction, travel-time lookup, MILP solving, dashboard export, and Table 2 export.
- `config.yaml`: central configuration for paths, seeds, STGNN, MILP weights, and experiment parameters.
- `requirements.txt`: Python dependencies for the reproducible environment.

### Model and experiments

- `src/stgnn/model.py`: real GCN+GRU implementation in PyTorch.
- `src/stgnn/traffic_dataset.py`: chronological temporal dataset creation.
- `src/stgnn/synthetic.py`: synthetic temporal traffic and adjacency generation.
- `src/stgnn/train.py`: training, validation, test MAE/RMSE, checkpointing, and travel-time matrix export.
- `src/experiments/ablation.py`: fair Euclidean, Network, and Synthetic-STGNN MILP comparison.
- `src/experiments/sensitivity.py`: deterministic weight-perturbation sensitivity analysis.
- `tests/test_stgnn.py`: focused model and synthetic-data tests.

### Data and outputs

- `Datos/*.zip`: observed spatial source layers available in this workspace.
- `Resultados/siting-results.csv`: current allocation output.
- `Resultados/siting-comparison.png`: current comparison figure.
- `outputs/metrics/*`: STGNN metrics, travel-time matrix, ablation metrics, sensitivity metrics, and manifests.
- `outputs/tables/*`: paper-ready result tables.
- `outputs/allocations/*`: allocation-level ablation and sensitivity outputs.
- `outputs/models/stgnn_best.pt`: best synthetic STGNN checkpoint.
- `outputs/synthetic/*`: synthetic temporal traffic dataset, metadata, and adjacency.

### Documentation

- `README.md`: execution and scientific-status guide.
- `DATA_AUDIT.md`: data provenance.
- `MANUSCRIPT_RECONCILIATION.md`: manuscript-code consistency notes.
- `PAPER_REVISION_GUIDE.md`: concrete manuscript edits by section, table, and figure.
- `EXPERIMENT_REPORT.md`: consolidated experiment report.
- `SYNTHETIC_EXPERIMENT_REPORT.md`: synthetic STGNN experiment details.
- `ABLATION_REPORT.md`: ablation study report.
- `SENSITIVITY_REPORT.md`: sensitivity study report.
- `results_analysis.md`: current result interpretation.

## Implementation Status

| Capability | Current status | Evidence / notes |
|---|---|---|
| Real GCN | Implemented | `src/stgnn/model.py` implements normalized graph convolution. |
| Real GRU | Implemented | `src/stgnn/model.py` uses `torch.nn.GRU` over temporal node embeddings. |
| STGNN training | Implemented | `src/stgnn/train.py` trains/evaluates with chronological splits. |
| MAE/RMSE calculation | Implemented | Test metrics are exported to `outputs/metrics/stgnn_test_metrics.json`. |
| Checkpoint save/load | Implemented | Best checkpoint is saved as `outputs/models/stgnn_best.pt`. |
| Synthetic traffic POC | Implemented | `outputs/synthetic/synthetic_traffic.csv` and adjacency are produced. |
| MILP formulation | Implemented | PuLP binary assignment model with capacity, hazard, water, and commute terms. |
| Profile 3 commute objective | Implemented | `optimization.delta_worker_commute_profile3` is consumed by the MILP. |
| Table 2 exports | Implemented | CSV, Markdown, and LaTeX exports are produced under `outputs/tables/`. |
| Fair ablation | Implemented | Euclidean, Network, and Synthetic-STGNN variants share constraints. |
| Sensitivity analysis | Implemented | Weight perturbations are exported under `outputs/metrics/` and `outputs/tables/`. |
| Reproducibility wrapper | Implemented | `run_pipeline.py --config config.yaml` runs the complete workflow. |

## Scientific Boundaries

| Claim area | Current evidence | Manuscript wording required |
|---|---|---|
| Traffic forecasting | Real GCN+GRU trained on synthetic observations | Controlled synthetic method validation, not empirical traffic validation. |
| CFE/JMAS capacity | Synthetic infrastructure proxies | Scenario assumptions unless official capacity data are added. |
| Candidate sites | Synthetic road-snapped candidate nodes | Synthetic candidate parcels/plots unless cadastral parcel data are added. |
| Hazard and water constraints | Synthetic stress-test geometries | Synthetic environmental exclusions unless official layers are added. |
| Profile 3 commute | Included in objective as a proxy term | Commute-aware proxy optimization, not observed worker commute optimization. |
| Table 2 | Produced from executable model outputs | Replace all old manuscript numbers with `outputs/tables/table2_results.*`. |

## Remaining Highest-Value Work

1. Replace synthetic temporal traffic with observed sensor or probe-speed time series.
2. Replace synthetic CFE/JMAS capacities with official infrastructure-capacity data.
3. Replace generated candidate points with cadastral or industrial-vacancy parcel data.
4. Replace synthetic hazard/water geometries with official flood, fault, aquifer, and water-stress layers.
5. Add a CI workflow after the GitHub repository layout is finalized.
