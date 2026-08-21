# Sensitivity Analysis Report

## Status

The repository now includes automated sensitivity analysis for the proposed Synthetic-STGNN MILP scenario.

This analysis is explicitly synthetic because the dynamic travel-time matrix is generated from a synthetic traffic experiment over the empirical road graph.

## Design

The experiment varies one objective weight at a time while holding the others fixed:

- `alpha`: CFE extension distance weight.
- `beta`: JMAS extension distance weight.
- `gamma`: synthetic dynamic border travel-time weight.
- `delta_worker_commute`: worker commute/accessibility weight for Profile 3.

Each parameter is varied by:

```text
-30%, -20%, -10%, 0%, +10%, +20%, +30%
```

Total runs:

```text
4 parameters x 7 variations = 28 MILP runs
```

## Outputs

| Output | Description |
|---|---|
| `outputs/metrics/sensitivity_runs.csv` | Raw run-level results. |
| `outputs/tables/sensitivity_summary.csv` | Aggregated summary by varied parameter. |
| `outputs/tables/sensitivity_summary.md` | Markdown summary table. |
| `outputs/allocations/sensitivity_allocations.csv` | Project assignments for every sensitivity run. |
| `outputs/metrics/sensitivity_manifest.json` | Scenario, baseline, and variation metadata. |

## Current Findings

After adding the Profile 3 worker-commute objective term, the current synthetic scenario is fully stable across the tested +/-30% perturbations:

- `max_selected_plot_set_changes = 0` for alpha, beta, and gamma.
- `max_selected_plot_set_changes = 0` for `delta_worker_commute`.
- `max_assignment_changes = 0` for all tested parameters.

This means the same project-to-parcel assignment remains selected across all tested perturbations.

Profile 3 average commute remains:

```text
2.9764 minutes
```

Allocation stability across the seven runs:

| Parameter | Stable runs | Stability |
|---|---:|---:|
| alpha | 7/7 | 1.0000 |
| beta | 7/7 | 1.0000 |
| gamma | 7/7 | 1.0000 |
| delta_worker_commute | 7/7 | 1.0000 |

Interpretation: the commute-aware baseline is robust within +/-30% local perturbations. The trade-off is that the commute-aware solution increases CFE/JMAS extension relative to the earlier no-commute solution, but it makes the Profile 3 labor-accessibility claim mathematically true in the optimization objective.
