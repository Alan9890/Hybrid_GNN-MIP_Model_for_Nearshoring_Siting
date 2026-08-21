# Ablation Study Report

## Status

The repository now includes a fair MILP ablation study for the synthetic traffic scenario.

This study is explicitly synthetic because the dynamic travel-time matrix comes from `outputs/metrics/travel_time_matrix.csv`, which is not observed historical traffic.

## Variants

| Variant | Network topology | Dynamic STGNN | CFE capacity | Environmental constraints |
|---|---:|---:|---:|---:|
| Euclidean MILP | No | No | Yes | Yes |
| Network MILP | Yes | No | Yes | Yes |
| Synthetic-STGNN MILP | Yes | Yes | Yes | Yes |

## Outputs

| Output | Description |
|---|---|
| `outputs/metrics/ablation_results.csv` | Raw metrics for every ablation variant. |
| `outputs/tables/ablation_summary.csv` | Manuscript-ready ablation summary table. |
| `outputs/tables/ablation_summary.md` | Markdown ablation summary table. |
| `outputs/allocations/ablation_allocations.csv` | Project-to-plot assignments by variant. |
| `outputs/metrics/ablation_manifest.json` | Variant definitions and objective weights. |

## Current Findings

With the current synthetic scenario and objective weights, all variants select the same set of 15 parcels, producing identical aggregate CFE/JMAS extension and commute metrics. The objective now includes a worker-commute term for Profile 3 (`LightMfg`), making the labor-accessibility claim operational rather than post-hoc.

- Profile 3 average commute is 2.9764 minutes in the current synthetic solution.
- Network MILP changes 2 project assignments relative to Euclidean MILP.
- Synthetic-STGNN MILP changes 5 project assignments relative to Euclidean MILP.
- Synthetic-STGNN MILP changes 3 project assignments relative to Network MILP.

This means the current ablation shows assignment-level sensitivity, but not yet a strong aggregate infrastructure improvement across variants. The commute term shifts the selected portfolio toward much lower worker-accessibility cost for Profile 3, at the expense of larger utility extension distances compared with the earlier no-commute objective.
