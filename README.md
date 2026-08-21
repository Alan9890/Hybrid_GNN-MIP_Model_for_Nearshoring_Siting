# Hybrid GNN-MIP Model for Nearshoring Siting

Proof of concept for industrial site selection in Ciudad Juarez, Chihuahua, under border-region infrastructure, mobility, hazard, and water-stress constraints.

## Scientific Status

This repository contains a reproducible method-validation pipeline:

- Real GIS inputs for the road graph and urban spatial context are loaded from `Datos/`.
- A real PyTorch GCN+GRU model is implemented in `src/stgnn/`.
- Temporal traffic observations are currently synthetic because empirical time-indexed traffic data are not available in this workspace.
- CFE/JMAS capacities, environmental exclusions, and traffic-time targets in this POC are synthetic scenario variables and must be described as such in the manuscript.
- The MILP consumes the travel-time matrix produced by the STGNN stage and includes a Profile 3 worker-commute term.

The current result is suitable for a controlled synthetic POC, not for claiming empirical traffic forecasting or official utility-capacity validation.

## Repository Structure

```text
Datos/                         Raw GIS and tabular ZIP inputs
Resultados/                    Main simulator outputs for dashboard and paper figures
outputs/
  allocations/                 Ablation and sensitivity allocation-level outputs
  metrics/                     STGNN metrics, ablation metrics, sensitivity metrics
  models/                      Best trained STGNN checkpoint
  synthetic/                   Synthetic temporal traffic dataset and adjacency
  tables/                      Paper-ready CSV, Markdown, and LaTeX tables
src/
  experiments/                 Ablation and sensitivity experiment runners
  stgnn/                       GCN+GRU model, dataset loader, trainer, synthetic generator
tests/                         Focused STGNN tests
config.yaml                    Central experiment configuration
run_pipeline.py                One-command orchestration
simulate_siting.py             GIS loading, graph routing, MILP solving, output generation
index.html                     Local dashboard
dashboard_data.js              Dashboard data exported by the simulator
```

## Quick Start

Use Python 3.12 on Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_pipeline.py --config config.yaml
```

Run the focused tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_stgnn.py -q
```

Force STGNN retraining instead of using the cached checkpoint:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --config config.yaml --force-stgnn-train
```

Open the dashboard after running the pipeline:

```powershell
.\run_dashboard.bat
```

Then visit `http://localhost:8000/index.html`.

## Current Reproducible Results

The main simulator exports Table 2 to:

- `outputs/tables/table2_results.csv`
- `outputs/tables/table2_results.md`
- `outputs/tables/table2_results.tex`

Current Table 2:

| Siting paradigm | CFE grid extension (m) | JMAS sewer extension (m) | Avg. commute/time (min) | CFE overloads | Hazard violations | Water-stress violations |
|---|---:|---:|---:|---:|---:|---:|
| Static GIS-AHP | 20,751.4 | 19,730.3 | 16.61 | 1 | 1 | 0 |
| Abstract MILP | 25,771.0 | 25,771.0 | 14.62 | 0 | 0 | 1 |
| Proposed GNN-MIP Simulator | 25,173.8 | 25,497.6 | 14.55 | 0 | 0 | 0 |

Current synthetic STGNN metrics:

| Metric | Value |
|---|---:|
| Synthetic MAE | 0.2248 min |
| Synthetic RMSE | 0.2741 min |
| Train samples | 159 |
| Validation samples | 34 |
| Test samples | 35 |

These MAE/RMSE values are synthetic method-validation metrics.

## Experiments

Run the ablation study:

```powershell
.\.venv\Scripts\python.exe -m src.experiments.ablation --config config.yaml
```

Outputs:

- `outputs/metrics/ablation_results.csv`
- `outputs/tables/ablation_summary.csv`
- `outputs/tables/ablation_summary.md`
- `outputs/allocations/ablation_allocations.csv`

The ablation compares Euclidean MILP, Network MILP, and Synthetic-STGNN MILP under the same capacity, hazard, and water-stress constraints. In the current run, the aggregate selected portfolio is the same across variants, while the parcel assignments differ. Synthetic-STGNN changes 5 assignments relative to Euclidean MILP and 3 relative to Network MILP.

Run the sensitivity study:

```powershell
.\.venv\Scripts\python.exe -m src.experiments.sensitivity --config config.yaml
```

Outputs:

- `outputs/metrics/sensitivity_runs.csv`
- `outputs/tables/sensitivity_summary.csv`
- `outputs/tables/sensitivity_summary.md`
- `outputs/allocations/sensitivity_allocations.csv`

The sensitivity stage varies `alpha`, `beta`, `gamma`, and `delta_worker_commute` by +/-10%, +/-20%, and +/-30%. In the current synthetic scenario, allocation stability is 1.0 across all tested perturbations.

## Paper Support Files

- `PAPER_REVISION_GUIDE.md`: exact manuscript edits by section, table, and figure.
- `EXPERIMENT_REPORT.md`: consolidated description of the synthetic STGNN, MILP, ablation, and sensitivity experiments.
- `MANUSCRIPT_RECONCILIATION.md`: manuscript-code consistency notes.
- `DATA_AUDIT.md`: data provenance audit.
- `results_analysis.md`: concise current result interpretation.
- `SYNTHETIC_EXPERIMENT_REPORT.md`: synthetic traffic experiment details.
- `ABLATION_REPORT.md`: fair ablation study details.
- `SENSITIVITY_REPORT.md`: sensitivity study details.

## Data Provenance

Observed inputs currently used:

- Road and urban GIS layers from `Datos/`.
- DENUE/IMIP-style local spatial context where available in the provided ZIP files.

Synthetic scenario inputs currently used:

- Temporal traffic observations.
- Parcel-level dynamic travel-time matrix.
- CFE/JMAS capacity and proximity proxies.
- Fault, flood, and water-stress stress-test geometries.

Any manuscript result derived from these variables should use language such as "controlled synthetic scenario over observed GIS layers" rather than "empirical validation."
