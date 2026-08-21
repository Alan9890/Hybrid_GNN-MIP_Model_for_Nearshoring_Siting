# Manuscript Reconciliation

## Statement requiring update: Table 2 values

Paper/README:
The current documentation reports fixed values such as CFE extension 36,665.7 m, JMAS extension 39,505.2 m, and average commute 17.67 min for the proposed model.

Repository result:
The previous script manually overwrote evaluated metrics to those values. After removing the overwrite, the table must use values generated from the current assignments.

Action:
Replace manuscript values with the generated values in `outputs/tables/table2_results.csv`, or clearly state the old values are not reproduced by the current code.

Reason:
Numerical results must be determined by the pipeline, not forced to match the manuscript.

## Statement requiring update: STGNN MAE/RMSE

Paper:
The manuscript mentions STGNN MAE/RMSE values.

Repository result:
A trainable GCN-GRU implementation, chronological split, checkpointing, and held-out MAE/RMSE code now exist. The repository can generate an explicitly synthetic temporal traffic experiment. However, no empirical temporal traffic dataset currently exists in the repository, so no empirical MAE/RMSE should be reported.

Action:
Replace the empirical MAE/RMSE claim with either empirical values after real temporal traffic data are added, or explicitly label any generated metrics as synthetic experiment results.

Reason:
No supervised traffic prediction evidence exists in the repository at this stage.

## Statement requiring update: empirical parcels and infrastructure

Paper:
The manuscript describes candidate parcels, CFE/JMAS infrastructure, hazards, and water stress as if they are observed model inputs.

Repository result:
Candidate plots, CFE substations, JMAS outlets, hazards, water stress, and congestion factors are generated in code.

Action:
Either replace these with empirical layers or revise the manuscript to describe the current implementation as a synthetic scenario over an observed road/neighborhood base.

Reason:
The available repository data do not support those empirical claims yet.

## Statement requiring update: Profile 3 worker commute optimization

Paper:
Labor-Intensive Manufacturing is optimized to minimize worker commute times.

Repository result:
The MILP now includes a Profile 3 worker-commute objective term controlled by `optimization.delta_worker_commute_profile3` in `config.yaml`. The current synthetic solution achieves Profile 3 average commute of 2.9764 minutes, but this is based on synthetic candidate parcels and colonia-centroid commute proxies.

Action:
Keep the optimization claim only if the manuscript labels the worker-accessibility input as a proxy/synthetic scenario, or replace the proxy with empirical worker/transit data.

Reason:
The commute term is now implemented, but the underlying accessibility data are not yet observed public-transit isochrones.
