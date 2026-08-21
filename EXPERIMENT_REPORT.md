# Experiment Report

## Scope

This repository implements a reproducible proof of concept for nearshoring industrial siting in Ciudad Juarez. The current experiment combines observed GIS base layers with explicitly synthetic scenario components.

## Data

Observed repository data:

- `Datos/Vialidad.zip`: major-road graph source.
- `Datos/Colonias.zip`: worker-accessibility proxy via neighborhood centroids.
- `Datos/Traza.zip`: urban block geometry, currently audited but not yet used as real vacant parcel candidates.
- `Datos/AreasVerdes.zip`, `Hidrantes.zip`, `Preescolares.zip`, `denue_08_*`: available observed layers, not fully integrated into the optimization model.

Synthetic or assumed components:

- Candidate parcels: 50 synthetic road-snapped candidates, 10 per planning sector.
- CFE substations: one synthetic capacity node per sector, 5,000 kVA each.
- JMAS outlets: synthetic sewer outlet nodes near sector centers.
- Hazards and water stress: synthetic geometric and zonal proxies.
- Traffic: synthetic temporal traffic over the observed major-road graph.

## STGNN

Implemented model:

- `src/stgnn/model.py`
- Dense GCN layer using normalized adjacency with self-loops.
- GRU over node-level temporal embeddings.
- MSE loss, Adam optimizer, chronological train/validation/test split, checkpointing, and held-out MAE/RMSE.

Current synthetic metrics:

| Metric | Value |
|---|---:|
| MAE | 0.2248 min |
| RMSE | 0.2741 min |
| Train samples | 159 |
| Validation samples | 34 |
| Test samples | 35 |

Outputs:

- `outputs/models/stgnn_best.pt`
- `outputs/metrics/stgnn_history.csv`
- `outputs/metrics/stgnn_test_metrics.json`
- `outputs/synthetic/synthetic_traffic.csv`
- `outputs/metrics/travel_time_matrix.csv`

## Optimization

The MILP assigns 15 industrial projects to 50 candidate parcels with:

- one assignment per project;
- at most one project per parcel;
- CFE capacity aggregation by nearest synthetic substation;
- hazard exclusion;
- water-stress exclusion for heavy-water projects;
- Profile 3 worker-commute objective term.

Profile 3 commute objective:

```yaml
optimization:
  delta_worker_commute_profile3: 2500.0
```

## Main Results

Generated Table 2:

| Model | CFE grid extension (m) | JMAS sewer extension (m) | Average commute/time (min) | CFE overloads | Hazard violations | Water-stress violations |
|---|---:|---:|---:|---:|---:|---:|
| Static GIS-AHP | 20,751.4 | 19,730.3 | 16.61 | 1 | 1 | 0 |
| Abstract MILP | 25,771.0 | 25,771.0 | 14.62 | 0 | 0 | 1 |
| Proposed GNN-MIP Simulator | 25,173.8 | 25,497.6 | 14.55 | 0 | 0 | 0 |

## Ablation

Variants:

- Euclidean MILP
- Network MILP
- Synthetic-STGNN MILP

Current finding:

- Synthetic-STGNN MILP changes 5 project assignments relative to Euclidean MILP.
- Synthetic-STGNN MILP changes 3 project assignments relative to Network MILP.
- Profile 3 average commute is 2.9764 minutes.

Outputs:

- `outputs/metrics/ablation_results.csv`
- `outputs/tables/ablation_summary.csv`
- `outputs/allocations/ablation_allocations.csv`

## Sensitivity

Parameters varied:

- `alpha`
- `beta`
- `gamma`
- `delta_worker_commute`

Variations:

- -30%, -20%, -10%, 0%, +10%, +20%, +30%

Runs:

- 28 MILP runs.

Current finding:

- allocation stability is 1.0 for all varied parameters under the current commute-aware baseline.

Outputs:

- `outputs/metrics/sensitivity_runs.csv`
- `outputs/tables/sensitivity_summary.csv`
- `outputs/allocations/sensitivity_allocations.csv`

## Reproduction

Recommended local environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_pipeline.py --config config.yaml
```

Force STGNN retraining:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --config config.yaml --force-stgnn-train
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_stgnn.py -q
```

## Limitations

- Synthetic traffic is not observed historical traffic.
- Candidate parcels are synthetic road-snapped points, not verified vacant parcel polygons.
- CFE/JMAS infrastructure nodes and capacities are synthetic assumptions.
- Hazards and water stress are synthetic proxies.
- Public-transit isochrones are not yet implemented; worker commute uses colonia centroid proximity.

