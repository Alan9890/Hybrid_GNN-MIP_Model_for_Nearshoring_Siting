# Synthetic STGNN Experiment Report

## Status

The repository now includes a reproducible synthetic traffic experiment over the empirical Ciudad Juarez major-road graph.

This experiment is explicitly synthetic. It must not be described as observed historical traffic.

## Generated Outputs

| Output | Description |
|---|---|
| `outputs/synthetic/synthetic_traffic.csv` | Synthetic temporal segment-level traffic observations. |
| `outputs/synthetic/synthetic_adjacency.npy` | Dense adjacency matrix for the synthetic sensor graph. |
| `outputs/synthetic/synthetic_traffic_metadata.json` | Provenance and scenario metadata. |
| `outputs/metrics/feature_schema.json` | STGNN feature schema for the synthetic experiment. |
| `outputs/metrics/travel_time_matrix.csv` | Synthetic parcel-to-border travel-time coefficients consumed by the MILP. |
| `outputs/metrics/stgnn_status.json` | Training/run status. |

## Scenario Design

- Road substrate: observed `Vialidad.zip`, filtered to major arterials where `V_PPAL == "SI"`.
- Synthetic sensor nodes: 64.
- Temporal periods: 240 hourly timestamps.
- Target: `travel_time_min`.
- Input CSV columns: `timestamp`, `road_segment_id`, `speed_kph`, `travel_time_min`.
- Congestion pattern: morning/evening peaks, weekly wave, bridge-proximity congestion, and seeded noise.
- Random seed: 42.

## Current Local Run

The local `.venv` environment uses Python 3.12 with PyTorch CPU. The synthetic data, travel-time matrix, model checkpoint, and held-out synthetic metrics were generated successfully.

The status and metrics are recorded in:

```text
outputs/metrics/stgnn_status.json
outputs/metrics/stgnn_test_metrics.json
```

Current synthetic test metrics:

| Metric | Value | Unit |
|---|---:|---|
| MAE | 0.2248 | minutes |
| RMSE | 0.2741 | minutes |
| Train samples | 159 | temporal windows |
| Validation samples | 34 | temporal windows |
| Test samples | 35 | temporal windows |

These are synthetic metrics only, not empirical traffic forecasting results.

## How To Train

Install dependencies, including PyTorch:

```bash
pip install -r requirements.txt
```

Then run:

```bash
.venv\Scripts\python.exe -m src.stgnn.train --config config.yaml --data-dir Datos --outputs-dir outputs
```

The stage trains `src.stgnn.model.GCNGRU`, saves a checkpoint, and writes held-out synthetic MAE/RMSE to:

```text
outputs/metrics/stgnn_test_metrics.json
```

For the full cached pipeline after training:

```bash
.venv\Scripts\python.exe run_pipeline.py --config config.yaml
```

To force STGNN retraining:

```bash
.venv\Scripts\python.exe run_pipeline.py --config config.yaml --force-stgnn-train
```

## MILP Integration

`simulate_siting.py` now checks for:

```text
outputs/metrics/travel_time_matrix.csv
```

When the file exists, the proposed MILP uses its `predicted_minutes` values as parcel-to-border travel-time coefficients.

In the current synthetic scenario, aggregate Table 2 values did not materially change because the objective remains dominated by land price and utility-distance terms. This is an experiment-design issue, not a runtime failure. The next refinement is to run an ablation/sensitivity pass with larger freight/dynamic-travel weights and report allocation stability.
