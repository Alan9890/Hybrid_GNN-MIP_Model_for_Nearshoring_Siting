# Current Results Analysis

This document summarizes the current reproducible proof-of-concept results. The experiment is a synthetic traffic scenario over the observed Ciudad Juarez major-road graph, not an empirical traffic validation.

## Current Table 2

| Model | CFE grid extension (m) | JMAS sewer extension (m) | Average commute/time (min) | CFE overloads | Hazard violations | Water-stress violations |
|---|---:|---:|---:|---:|---:|---:|
| Static GIS-AHP | 20,751.4 | 19,730.3 | 16.61 | 1 | 1 | 0 |
| Abstract MILP | 25,771.0 | 25,771.0 | 14.62 | 0 | 0 | 1 |
| Proposed GNN-MIP Simulator | 25,173.8 | 25,497.6 | 14.55 | 0 | 0 | 0 |

## STGNN Synthetic Metrics

| Metric | Value |
|---|---:|
| Synthetic MAE | 0.2248 min |
| Synthetic RMSE | 0.2741 min |
| Train samples | 159 |
| Validation samples | 34 |
| Test samples | 35 |

These metrics are produced from synthetic temporal traffic observations and must be described as synthetic.

## Ablation Summary

The ablation compares Euclidean MILP, Network MILP, and Synthetic-STGNN MILP under the same CFE capacity, water-stress, and hazard constraints.

Current finding: all three ablation variants select the same aggregate infrastructure portfolio under the commute-aware objective, but the project-to-parcel assignments differ. Synthetic-STGNN MILP changes 5 project assignments relative to Euclidean MILP and 3 relative to Network MILP.

Profile 3 average commute in the ablation is 2.9764 minutes, because the MILP objective now includes `delta_worker_commute_profile3`.

## Sensitivity Summary

The sensitivity study varies `alpha`, `beta`, `gamma`, and `delta_worker_commute` by +/-10%, +/-20%, and +/-30%.

Current finding: the commute-aware baseline is stable under the tested perturbations. Allocation stability is 1.0 for all four varied parameters.

## Interpretation

The current POC supports a methodological claim: a GCN+GRU STGNN stage, dynamic travel-time matrix, MILP allocation, ablation, and sensitivity analysis can be executed reproducibly. It does not yet support field-validation claims about observed historical traffic or official utility/hazard datasets.
