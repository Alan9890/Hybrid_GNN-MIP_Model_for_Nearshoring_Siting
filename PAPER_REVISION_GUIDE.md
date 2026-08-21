# Paper Revision Guide

This guide lists specific edits required for `Articulo_08_17_26.pdf` based on the current reproducible repository.

## Global Edits

Replace empirical language with synthetic-scenario language wherever appropriate.

Use:

> controlled synthetic traffic scenario over the observed Ciudad Juarez major-road graph

Do not use:

> historical segment-speed traffic profiles

unless empirical temporal traffic data are added.

Use `kVA` instead of `KVA`. Use `siting` instead of `sitting`. Correct `reset gate`, not `restet gaye`.

## Title Page / Template

Section: first page header and author block.

Change:

- `F. Author and S. Author`
- `Contribution Title (shortened if too long)`
- `Princeton University`
- `Springer Heidelberg`
- `lncs@springer.com`

Replace with real author affiliations, emails, and running head required by MICAI/LNCS.

## Abstract

Current issue: the abstract implies empirical vacant parcels, empirical infrastructure, public-transit accessibility, and learned dynamic traffic.

Recommended replacement sentence:

> We evaluate the current proof of concept through a controlled synthetic traffic scenario over the observed Ciudad Juarez major-road graph, combining reproducible GCN-GRU forecasting, MILP allocation, ablation, and sensitivity analysis.

Add limitation sentence:

> Because segment-level historical traffic, verified vacant parcel inventories, and official utility-capacity layers were not available in the repository, traffic, candidate parcels, utility nodes, and hazard constraints are explicitly modeled as synthetic scenario components.

## Section 1.3 Contributions

Change contribution 4.

Current:

> Validation of the proposed methodology through a case study using vacant industrial parcels in Ciudad Juarez, Mexico.

Replace with:

> Reproducible proof-of-concept evaluation on observed Ciudad Juarez road and neighborhood GIS layers with explicitly labeled synthetic traffic, parcel, utility, and hazard scenario components.

## Section 3.2 STGNN

Current issue: the paper says the STGNN was trained using historical segment-speed traffic profiles from `VialidadWgs84.shp` and reports MAE 1.84 and RMSE 2.51.

Replace the training paragraph with:

> The GCN-GRU architecture was implemented as a trainable STGNN module using a normalized graph convolution followed by a GRU temporal layer. Because historical segment-level speed observations were not available, we generated a controlled synthetic temporal traffic scenario over the observed major-road graph. The synthetic dataset contains hourly segment-level speed and travel-time observations, with morning/evening peak patterns, bridge-proximity congestion, weekly variation, and seeded noise. The model was trained with MSE loss and Adam using a chronological train/validation/test split. On the held-out synthetic test set, the model obtained MAE = 0.2248 min and RMSE = 0.2741 min. These metrics validate the computational pipeline under synthetic conditions and should not be interpreted as empirical traffic forecasting performance.

Remove or replace:

- `MAE = 1.84 minutes`
- `RMSE = 2.51 minutes`
- `historical segment-speed traffic profiles extracted from IMIP primary road registry`

## Section 3.3 Feature Vector

Replace empirical wording with:

> In the current proof of concept, logistics features are derived from synthetic dynamic travel-time coefficients, worker accessibility is approximated through network travel time to colonia centroids, utility features are represented by synthetic CFE/JMAS connection nodes, and environmental features are represented through synthetic hazard and water-stress proxies.

Add:

> The model interfaces are designed so empirical CFE, JMAS, hazard, water-stress, and public-transit layers can replace these proxies in future runs.

## Section 3.6 Evaluation Scenario

Replace the claim that 50 vacant plots were extracted from `Traza_Wgs84.shp` with:

> The current scenario uses 50 synthetic candidate locations sampled deterministically from road-network nodes around five planning sectors. The road and neighborhood layers are observed GIS inputs, while candidate parcels, CFE substations, JMAS outlets, hazards, and water-stress values are synthetic scenario assumptions.

Replace CFE/JMAS DENUE filtering claim with:

> five synthetic CFE capacity nodes and five synthetic JMAS outlet nodes were generated near planning-sector centers for proof-of-concept testing.

## Section 3.6 Project Profiles

Add:

> For Profile 3, worker accessibility is included directly in the MILP objective through a commute coefficient `delta_worker_commute`, applied only to labor-intensive manufacturing projects.

Clarify:

> In the current synthetic scenario, this commute term uses a colonia-centroid network-accessibility proxy rather than public-transit isochrones.

## Section 3.7 Baselines

Add a new paragraph:

> In addition to the original GIS-AHP and Abstract MILP comparison, we run a fair ablation study with identical feasibility constraints across Euclidean MILP, Network MILP, and Synthetic-STGNN MILP variants. This isolates the effect of network topology and synthetic dynamic travel times.

## Section 3.8 Table 2

Replace the entire Table 2 with:

| Model Paradigm | CFE Grid Ext (m) | JMAS Sewer Ext (m) | Avg. Commute/Time (min) | Substation Overloads | Hazard Violations | Water Violations |
|---|---:|---:|---:|---:|---:|---:|
| Static GIS-AHP | 20,751.4 | 19,730.3 | 16.61 | 1 | 1 | 0 |
| Abstract MILP | 25,771.0 | 25,771.0 | 14.62 | 0 | 0 | 1 |
| Proposed GNN-MIP Simulator | 25,173.8 | 25,497.6 | 14.55 | 0 | 0 | 0 |

Replace discussion:

> The proposed method reduces average commute/time relative to both baselines while maintaining zero overload, hazard, and water-stress violations. This reduction is achieved at the cost of larger utility extension distances than the Static GIS-AHP baseline, reflecting a trade-off introduced by feasibility constraints and the Profile 3 commute objective.

Remove old claims:

- 36,665.7 m
- 39,505.2 m
- 17.67 min
- 26.25% reduction
- 36.6% improvement
- 10.14% / 11.92% infrastructure savings

## Add New Table: STGNN Synthetic Metrics

Place after Section 3.2 or before Table 2.

| Metric | Value | Interpretation |
|---|---:|---|
| MAE | 0.2248 min | Synthetic held-out test set |
| RMSE | 0.2741 min | Synthetic held-out test set |
| Train samples | 159 | Chronological split |
| Validation samples | 34 | Chronological split |
| Test samples | 35 | Chronological split |

Caption:

> Synthetic STGNN forecasting metrics. Values are computed from a controlled synthetic traffic scenario and are not empirical field-validation metrics.

## Add New Table: Ablation Study

Use `outputs/tables/ablation_summary.csv`.

Recommended compact table:

| Model | Network topology | Dynamic STGNN | CFE Ext (m) | JMAS Ext (m) | Avg. Commute | Profile 3 Commute | Assignment Changes vs Euclidean |
|---|---:|---:|---:|---:|---:|---:|---:|
| Euclidean MILP | No | No | 25,575.6 | 25,872.1 | 14.34 | 2.9764 | 0 |
| Network MILP | Yes | No | 25,575.6 | 25,872.1 | 14.34 | 2.9764 | 2 |
| Synthetic-STGNN MILP | Yes | Yes | 25,575.6 | 25,872.1 | 14.34 | 2.9764 | 5 |

Discussion:

> The selected parcel portfolio remains stable, but project-to-parcel assignments change across variants, indicating assignment-level sensitivity to topology and synthetic dynamic travel-time coefficients.

## Section 3.9 Sensitivity Analysis

Replace 30 independent simulations with:

> We conduct 28 deterministic sensitivity runs by varying four objective parameters (`alpha`, `beta`, `gamma`, and `delta_worker_commute`) by -30%, -20%, -10%, 0%, +10%, +20%, and +30%.

Add result:

> Under the current commute-aware synthetic scenario, allocation stability is 1.0 for all four varied parameters. This indicates local robustness of the selected assignment under +/-30% perturbations.

Use `outputs/tables/sensitivity_summary.csv`.

## Section 3.10 Empirical and External Field Validation

Replace heading with:

> Qualitative Spatial Plausibility

Add:

> These comparisons are qualitative plausibility checks and are not formal predictive validation.

Remove or cite with exact source:

- 40% heavy commercial vehicle traffic increase
- 45% worker population concentration

## Figure Changes

Figure 1:

- Keep as architecture if it matches the current pipeline.
- Update labels to show "synthetic traffic scenario" rather than "historical traffic".

Figure 2:

- Keep GCN-GRU architecture.
- Caption must say synthetic traffic experiment unless empirical traffic data are added.

Figure 3:

- Use the regenerated `Resultados/siting-comparison.png`.
- Do not use old manually edited figures or local absolute paths.

Add optional figures:

- STGNN training curve from `outputs/metrics/stgnn_history.csv`.
- Sensitivity stability chart from `outputs/tables/sensitivity_summary.csv`.

## Conclusion

Replace empirical validation language with:

> The current implementation demonstrates a reproducible proof of concept under a controlled synthetic traffic scenario over observed GIS road and neighborhood layers. Future work will replace synthetic traffic, parcel, utility, hazard, and accessibility proxies with empirical municipal and infrastructure datasets.

