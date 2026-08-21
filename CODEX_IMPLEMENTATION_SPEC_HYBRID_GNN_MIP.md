# Codex Implementation Specification
## Hybrid GNN-MIP Model for Nearshoring Siting under Border Constraints

### Purpose

This repository must become a **scientifically reproducible implementation** of the methodology described in the manuscript:

**“Hybrid GNN-MIP Model for Nearshoring Siting under Border Constraints.”**

The objective is **not** to reproduce manuscript numbers by manually assigning them.  
The objective is to implement the methodology faithfully, execute it on the available data, and generate the manuscript tables, figures, metrics, and intermediate outputs from code.

If the available data cannot support a claim in the manuscript, **do not fabricate or silently synthesize missing evidence**. Instead:

1. document the missing data;
2. implement the pipeline so that the real data can be inserted later;
3. clearly identify any synthetic/simulated component;
4. generate a `MANUSCRIPT_RECONCILIATION.md` file describing which manuscript statements or numerical values must be updated.

---

# 1. Non-Negotiable Scientific Rules

## 1.1 No hardcoded experimental results

Remove any code that manually overwrites calculated metrics to make them equal to manuscript values.

Examples of prohibited behavior:

```python
results["commute"] = 17.67
results["cfe_extension"] = 36665.7
```

or:

```python
# calibrate values to match paper
```

All reported values must be generated from the pipeline.

This applies especially to:

- CFE grid extension distance;
- JMAS sewer extension distance;
- average commute/travel time;
- CFE substation overloads;
- environmental hazard violations;
- water-stress violations;
- MAE;
- RMSE;
- percentage improvements;
- sensitivity-analysis values.

---

## 1.2 Do not fabricate unavailable GIS or traffic data

Before implementing the model, inspect all repository datasets and produce:

```text
data_inventory.csv
DATA_AUDIT.md
```

For every dataset/layer, record:

- filename;
- source;
- geometry type;
- coordinate reference system;
- number of records;
- relevant columns;
- missing values;
- whether the layer is observed/empirical or synthetic;
- role in the model.

The manuscript references, among others:

- `VialidadWgs84.shp`
- `Traza_Wgs84.shp`
- IMIP spatial registries
- CFE-related utility information
- JMAS sewer information
- DENUE utility records
- geological-fault information
- flood/runoff information
- water-stress information
- road/traffic information

Do not assume that a variable exists merely because the manuscript mentions it.

If historical speed observations required for STGNN training do not exist in the repository, stop the training stage with a clear explanation or use an explicitly labeled synthetic experiment. Never describe synthetic traffic as observed historical traffic.

---

# 2. Repository Audit Before Modification

Before modifying algorithms, inspect the entire repository.

Generate:

```text
REPOSITORY_AUDIT.md
```

The audit must contain:

## Existing files
List:

- Python scripts
- notebooks
- GIS files
- CSV files
- generated figures
- generated results
- README files
- dependency files

## Existing implementation
Determine whether the repository currently contains:

- a real GCN;
- a real GRU;
- STGNN training;
- train/validation/test splitting;
- loss optimization;
- MAE calculation;
- RMSE calculation;
- checkpoint saving/loading;
- MIP/MILP formulation;
- GIS-AHP baseline;
- abstract MILP baseline;
- sensitivity analysis;
- environmental constraints.

## Manuscript-code inconsistencies

Create a table:

| Manuscript claim | Current implementation | Status | Required action |
|---|---|---|---|

Do not hide inconsistencies.

---

# 3. Target Scientific Pipeline

The final architecture should follow the manuscript:

```text
Raw GIS / infrastructure / traffic data
                |
                v
       Data validation & CRS
                |
                v
      Multi-layer spatial graph
                |
                v
      STGNN: GCN + GRU
                |
                v
 Dynamic travel-time coefficients
                |
                v
 Multi-dimensional parcel features
                |
                v
            MILP
                |
                v
 Facility allocations
                |
                v
Evaluation / baselines / sensitivity
                |
                v
 Tables + figures + reproducibility report
```

The main components described in the manuscript are:

1. Multi-layer spatial graph construction.
2. Spatio-Temporal Graph Neural Network.
3. Multi-dimensional infrastructure feature vector.
4. Mixed-Integer siting optimization.
5. Baseline comparison.
6. Sensitivity analysis.
7. Spatial visualization.

---

# 4. Recommended Repository Structure

This structure is an implementation recommendation intended to make the manuscript reproducible.

```text
Hybrid_GNN-MIP_Model_for_Nearshoring_Siting/
│
├── README.md
├── requirements.txt
├── pyproject.toml                 # optional
├── config.yaml
├── run_pipeline.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── synthetic/                # ONLY if explicitly labeled
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/
│   │   ├── audit.py
│   │   ├── loaders.py
│   │   ├── preprocessing.py
│   │   └── traffic_dataset.py
│   │
│   ├── spatial/
│   │   ├── graph_builder.py
│   │   ├── routing.py
│   │   ├── hazards.py
│   │   └── parcel_features.py
│   │
│   ├── stgnn/
│   │   ├── model.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── inference.py
│   │
│   ├── optimization/
│   │   ├── milp.py
│   │   ├── constraints.py
│   │   └── objective.py
│   │
│   ├── baselines/
│   │   ├── gis_ahp.py
│   │   ├── euclidean_milp.py
│   │   └── network_milp.py
│   │
│   ├── experiments/
│   │   ├── main_experiment.py
│   │   ├── ablation.py
│   │   └── sensitivity.py
│   │
│   └── visualization/
│       ├── maps.py
│       └── plots.py
│
├── outputs/
│   ├── models/
│   ├── metrics/
│   ├── tables/
│   ├── figures/
│   └── allocations/
│
├── tests/
│   ├── test_graph.py
│   ├── test_stgnn.py
│   ├── test_milp.py
│   └── test_reproducibility.py
│
├── DATA_AUDIT.md
├── REPOSITORY_AUDIT.md
├── EXPERIMENT_REPORT.md
└── MANUSCRIPT_RECONCILIATION.md
```

---

# 5. Configuration

Move experimental constants into one configuration file.

Example:

```yaml
random_seed: 42

spatial:
  target_crs: "EPSG:32613"

candidates:
  requested_count: 50

projects:
  requested_count: 15

stgnn:
  learning_rate: 0.001
  batch_size: 64
  weight_decay: 0.00001
  epochs: 200
  early_stopping_patience: 20

optimization:
  solver: "CBC"

sensitivity:
  variations:
    - -0.30
    - -0.20
    - -0.10
    - 0.00
    - 0.10
    - 0.20
    - 0.30
```

Important:

The values above reproduce parameters explicitly mentioned in the manuscript where applicable.  
Do not invent missing physical parameters simply to obtain a desired result.

---

# 6. Spatial Data and Coordinate System

The manuscript states that spatial data are projected to:

```text
WGS84 / UTM Zone 13N
EPSG:32613
```

All metric distance calculations must therefore use a projected CRS.

Create validation checks that reject distance computations in latitude/longitude.

Example:

```python
assert gdf.crs is not None
assert gdf.crs.to_epsg() == 32613
```

All routing distances should have explicit units.

Recommended internal convention:

```text
distance: meters
travel time: minutes
electrical capacity: kVA
```

---

# 7. Multi-Layer Spatial Graph

Implement the graph described in Section 3.1:

\[
\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{W})
\]

with:

\[
\mathcal{V} =
\mathcal{V}_{road}
\cup
\mathcal{V}_{power}
\cup
\mathcal{V}_{sewer}
\cup
\mathcal{V}_{land}
\]

Represent at minimum:

- road/intersection nodes;
- candidate industrial parcels;
- CFE connection/substation nodes;
- JMAS connection/collector nodes.

Road edges must use topological/network connectivity, not merely Euclidean distance.

Utility distance terms must be computed through the selected routing/linkage network where the data support this.

---

# 8. Candidate Parcels

The manuscript describes 50 candidate vacant industrial parcels distributed across five planning sectors:

- Norte Centro;
- Oriente;
- Sur;
- Sur Oriente;
- San Jerónimo.

Codex must first verify whether the repository actually contains parcel polygons that support this claim.

## If real parcels exist

Select candidates deterministically and document the selection criteria.

Prefer:

```text
parcel_id
geometry
sector
area
land_price
hazard indicators
utility proximity
```

## If real candidate parcels do not exist

Do not silently replace them with random road nodes while continuing to call them empirical vacant parcels.

Instead:

- create an explicit `synthetic` scenario;
- label it in outputs;
- document the generation procedure;
- list the manuscript wording that must change.

---

# 9. STGNN — Required Real Implementation

The manuscript explicitly describes an STGNN formed by:

```text
GCN + GRU
```

Therefore the final repository must contain an actual trainable implementation if the paper is to retain this claim.

Recommended implementation:

- PyTorch;
- PyTorch Geometric, or a transparent custom GCN implementation.

Do not use a fixed congestion multiplier and call it an STGNN.

---

# 10. GCN Component

Implement the graph convolution described by the manuscript:

\[
H_t^{(l+1)}
=
\sigma
\left(
\tilde{D}^{-1/2}
\tilde{A}
\tilde{D}^{-1/2}
H_t^{(l)}
W^{(l)}
\right)
\]

where:

\[
\tilde{A} = A + I
\]

and:

\[
\tilde{D}_{ii}
=
\sum_j \tilde{A}_{ij}
\]

Use ReLU unless there is a documented reason to change it.

Node features must be documented.

Do not use coordinates alone without explaining why.

Possible features should be selected only when supported by available data, for example:

- coordinates;
- segment length;
- road class;
- observed speed;
- time-of-day information;
- directionality;
- traffic state.

Create:

```text
outputs/metrics/feature_schema.json
```

---

# 11. GRU Component

Use the GCN output sequence as input to a GRU.

The conceptual model should correspond to the manuscript equations:

\[
z_t =
\sigma(W_z[H_t,h_{t-1}] + b_z)
\]

\[
r_t =
\sigma(W_r[H_t,h_{t-1}] + b_r)
\]

\[
\tilde{h}_t =
\tanh(W_h[H_t,r_t \odot h_{t-1}] + b_h)
\]

\[
h_t =
z_t \odot h_{t-1}
+
(1-z_t)\odot\tilde{h}_t
\]

It is acceptable to use a standard framework GRU implementation as long as its role is documented.

---

# 12. Traffic Dataset

The STGNN needs supervised temporal targets.

Before training, identify what the repository actually contains.

A valid temporal dataset should conceptually contain something similar to:

```text
timestamp
road_segment_id
speed
travel_time
road attributes...
```

Create temporal samples:

```text
X[t-window:t] -> y[t+1]
```

Do not randomly split temporally dependent observations across train and test.

Prefer a chronological split:

```text
Train: earliest ~70%
Validation: next ~15%
Test: latest ~15%
```

Document exact percentages and date ranges.

---

# 13. STGNN Training

The manuscript specifies:

```text
Loss: Mean Squared Error
Optimizer: Adam
Learning rate: 1e-3
Batch size: 64
L2 / weight decay: 1e-5
```

Implement these values as the manuscript baseline configuration.

Use:

- deterministic random seed;
- early stopping;
- checkpointing;
- best validation model restoration.

Save:

```text
outputs/models/stgnn_best.pt
outputs/metrics/stgnn_history.csv
outputs/metrics/stgnn_test_metrics.json
```

---

# 14. STGNN Metrics

Calculate from held-out test data:

\[
MAE =
\frac{1}{n}\sum_i |y_i-\hat{y}_i|
\]

\[
RMSE =
\sqrt{
\frac{1}{n}
\sum_i (y_i-\hat{y}_i)^2
}
\]

The manuscript currently mentions:

```text
MAE = 1.84 minutes
RMSE = 2.51 minutes
```

These values are **not targets that the code is allowed to force**.

Run the real experiment.

If the values differ, store the real values and write the required manuscript update in:

```text
MANUSCRIPT_RECONCILIATION.md
```

---

# 15. Dynamic Travel-Time Matrix

The trained STGNN must produce the travel-time information consumed downstream by the optimizer.

The manuscript defines:

\[
T_{jk}(t)
\]

as the dynamic travel time from candidate parcel \(j\) to border crossing \(k\).

Relevant border crossings include:

- Zaragoza–Ysleta;
- Córdova/Américas;
- Jerónimo–Santa Teresa.

Create a reproducible inference process such as:

```python
T_jk = stgnn_predict(
    graph=road_graph,
    origin=parcel,
    destination=border_crossing,
    timestamp=peak_time,
)
```

Save:

```text
outputs/metrics/travel_time_matrix.csv
```

Rows should contain at least:

```text
parcel_id
border_crossing
timestamp_or_scenario
predicted_minutes
baseline_minutes
```

Do not apply arbitrary 1.5x–2.4x factors and describe those factors as learned STGNN outputs unless they are empirically obtained from the trained model.

---

# 16. Multi-Dimensional Parcel Feature Vector

Implement the manuscript feature structure:

\[
X_{infra} =
[
X_{log},
X_{util},
X_{env}
]
\]

## Logistics features

Where supported:

- dynamic travel time to Zaragoza;
- dynamic travel time to Américas;
- dynamic travel time to Santa Teresa;
- worker commute/accessibility metric.

## Utility features

- network distance to CFE;
- available or modeled CFE capacity;
- network distance to JMAS.

## Environmental features

- geological-fault indicator/distance;
- flood susceptibility;
- water-stress indicator/category.

Generate:

```text
outputs/metrics/parcel_feature_matrix.csv
```

---

# 17. Worker Commute Variable

The manuscript states that labor-intensive manufacturing is optimized in relation to worker accessibility/commute.

Therefore, if the manuscript retains that statement, commute cannot be only a post-hoc evaluation metric.

Define a commute coefficient such as:

\[
C_j^{worker}
\]

or, if project-specific:

\[
C_{jp}^{worker}
\]

and include it in the optimization objective for the appropriate project profiles.

For example:

\[
+
\delta_p
C_j^{worker}
z_{jp}
\]

with project/profile-dependent \(\delta_p\).

Do not invent public-transit isochrones if no transit dataset exists. If unavailable, explicitly document the proxy used.

---

# 18. MILP Decision Variables

Use binary assignment variables:

\[
z_{jp}
=
\begin{cases}
1 & \text{if project } p \text{ is assigned to parcel } j\\
0 & \text{otherwise}
\end{cases}
\]

Indices:

```text
j = candidate parcel
p = industrial project
k = border crossing
i = utility/substation node when needed
```

---

# 19. MILP Objective Function

The manuscript conceptually minimizes:

\[
\sum_{j,p} C_j^{land}z_{jp}
+
\alpha
\sum_{j,p} d_{CFE}(j)z_{jp}
+
\beta
\sum_{j,p} d_{JMAS}(j)z_{jp}
+
\gamma
\sum_{j,p,k}
T_{jk}(t)F_pz_{jp}
\]

If worker commute is truly part of the optimization, extend the implemented objective transparently:

\[
+
\sum_{j,p}
\delta_p C_j^{worker}z_{jp}
\]

Every objective coefficient must have:

- a name;
- a unit;
- a source;
- a rationale;
- a value recorded in configuration.

Generate:

```text
outputs/metrics/objective_parameters.csv
```

---

# 20. MILP Constraints

## 20.1 Single allocation

Each project must be assigned to exactly one parcel:

\[
\sum_j z_{jp}=1
\quad
\forall p
\]

## 20.2 Parcel exclusivity

Each parcel hosts at most one project:

\[
\sum_p z_{jp}\leq1
\quad
\forall j
\]

## 20.3 Electrical capacity

The current manuscript equation must be checked carefully.

The correct implementation must aggregate **all projects assigned to parcels served by the same CFE substation**.

Conceptually:

\[
\sum_{j,p}
K_p
a_{ji}
z_{jp}
\leq
Cap_i
\quad
\forall i
\]

where:

```text
a_ji = 1 if parcel j is connected/assigned to substation i
K_p  = power requirement of project p
Cap_i = residual capacity of substation i
```

Do not enforce capacity independently per parcel if several parcels use the same substation.

---

# 21. Environmental Exclusion Constraints

If a parcel is inside an excluded geological-fault buffer:

\[
z_{jp}=0
\]

for all projects.

Similarly for high flood-risk exclusion zones.

Implement this using explicit eligibility masks where possible:

```python
eligible[j, p] = False
```

rather than multiplying binary decision variables by constants in a way that obscures logic.

---

# 22. Water-Stress Constraint

For water-intensive projects, prohibit parcels exceeding the selected water-stress threshold.

Use a clear implementation such as:

```python
if project.water_intensive and parcel.water_stress > lambda_threshold:
    model += z[j, p] == 0
```

Record the threshold and source in configuration.

---

# 23. Industrial Project Profiles

The manuscript describes 15 projects across three profiles:

## Profile 1 — Heavy Assembly

Characteristics described in the manuscript:

- high electrical demand;
- significant sewer requirements;
- water-intensive;
- strict utility and water-stress constraints.

The manuscript mentions approximately:

```text
2,500–5,000 kVA
```

for Heavy Assembly.

If the existing code uses different values, reconcile the implementation and manuscript.

Do not choose power loads merely because they make the optimization feasible.

If realistic capacities make the MILP infeasible, report infeasibility and investigate the model/data assumptions.

---

## Profile 2 — Logistics Warehouses

Emphasize:

- border travel time;
- freight movement;
- dynamic congestion sensitivity.

The manuscript mentions approximately:

```text
30–80 heavy truck movements/day
```

Represent freight intensity explicitly.

---

## Profile 3 — Labor-Intensive Manufacturing

Emphasize:

- worker accessibility;
- commute time;
- transit/residential proximity where supported by data.

This must be represented in the objective or constraints if the paper claims it is optimized.

---

# 24. Baselines

The experimental comparison must not give the proposed method an unfair structural advantage.

Implement at least:

## Baseline A — GIS-AHP

A transparent static multi-criteria method.

Document:

- criteria;
- normalization;
- pairwise matrix or weights;
- consistency ratio if a true AHP is used;
- ranking procedure.

Do not call a simple weighted sum “AHP” unless the AHP pairwise process is actually implemented.

---

## Baseline B — Euclidean MILP

Use:

- same project set;
- same candidate parcels;
- same capacity constraints;
- same environmental constraints;
- same land costs;

but use Euclidean/static transportation and utility distance assumptions.

This isolates the effect of topology/dynamic representation.

---

## Baseline C — Network MILP / Ablation

Use:

- actual network shortest paths;
- static/free-flow traffic;
- same MILP constraints as the proposed model.

This isolates the added contribution of the STGNN.

---

## Proposed — STGNN-MILP

Use:

- network topology;
- trained dynamic travel-time model;
- identical feasibility constraints.

---

# 25. Fair Ablation Study

Generate a table similar to:

| Model | Network topology | Dynamic STGNN | CFE capacity | Environmental constraints |
|---|---:|---:|---:|---:|
| GIS-AHP | No | No | depends on baseline definition | depends |
| Euclidean MILP | No | No | Yes | Yes |
| Network MILP | Yes | No | Yes | Yes |
| STGNN-MILP | Yes | Yes | Yes | Yes |

The key scientific comparison should be:

```text
Euclidean MILP -> Network MILP -> STGNN-MILP
```

because it isolates:

1. benefit from real network topology;
2. additional benefit from dynamic learned traffic information.

---

# 26. Evaluation Metrics

Calculate all metrics directly from final assignments.

At minimum:

```text
CFE grid extension (m)
JMAS sewer extension (m)
average commute/travel time (min)
substation overload count
hazard violation count
water-stress violation count
objective value
solver status
solver runtime
```

Recommended additional metrics:

```text
mean freight travel time
95th percentile freight travel time
total land cost
total infrastructure distance
maximum substation utilization
mean substation utilization
```

---

# 27. Recalculate Table 2

Do not preserve manuscript Table 2 values manually.

Generate:

```text
outputs/tables/table2_results.csv
outputs/tables/table2_results.md
outputs/tables/table2_results.tex
```

The table must be produced from a script.

Example:

```bash
python -m src.experiments.main_experiment
```

Then:

```text
table2_results.csv
```

must contain the exact values used in the manuscript.

If actual values differ from the current manuscript, do not alter the code to recover the manuscript numbers.

Update:

```text
MANUSCRIPT_RECONCILIATION.md
```

instead.

---

# 28. Percentage Improvements

Never hardcode improvement percentages.

Calculate them.

For a metric \(M\):

\[
Improvement =
\frac{
M_{baseline}-M_{proposed}
}{
M_{baseline}
}
\times100
\]

State which baseline is being used.

If two baselines exist, report improvements against each separately.

---

# 29. Sensitivity Analysis

The manuscript describes variation of objective weights:

```text
±10%
±20%
±30%
```

Implement it as an automated experiment.

For every parameter variation:

1. solve the MILP;
2. record assignment;
3. record objective;
4. record utility distances;
5. record travel times;
6. record feasibility/violations;
7. measure allocation stability.

Save raw results:

```text
outputs/metrics/sensitivity_runs.csv
```

and aggregate results:

```text
outputs/tables/sensitivity_summary.csv
```

Do not state “30 independent simulations” unless 30 actual runs or scenarios are executed and logged.

---

# 30. Repeated Experiments and Random Seeds

Any stochastic component must use fixed and documented seeds.

Recommended:

```text
42
123
2026
7
99
```

For neural-network evaluation, where computationally feasible, use multiple seeds and report:

```text
mean ± standard deviation
```

Do not use randomness to tune results toward the manuscript.

---

# 31. Statistical Integrity

If the same deterministic MILP and same deterministic coefficients are solved repeatedly, do not describe those repetitions as “independent simulations.”

Repeated runs are meaningful only if something varies, such as:

- random seed;
- synthetic scenario;
- demand realization;
- traffic sample;
- parameter perturbation;
- data split.

Clearly define what changes between runs.

---

# 32. External / Field Validation

The manuscript contains statements comparing model recommendations with observed development patterns in Ciudad Juárez.

Do not treat qualitative geographic agreement as predictive validation unless it is formally measured.

Separate:

```text
Quantitative validation
```

from:

```text
Qualitative spatial plausibility / external consistency
```

If external claims such as traffic-growth percentages or worker-concentration percentages cannot be traced to repository evidence or a cited source, flag them in:

```text
MANUSCRIPT_RECONCILIATION.md
```

---

# 33. Maps and Figures

Generate figures programmatically.

Required outputs should include, where data permit:

```text
road graph
candidate parcels
CFE nodes
JMAS nodes
hazard layers
selected parcels
baseline vs proposed allocations
STGNN training curves
STGNN prediction-vs-actual plot
sensitivity analysis plots
```

Save high-resolution files:

```text
PNG: >= 300 dpi
PDF/SVG: preferred for manuscript figures
```

Do not use manually edited figures when the same figure can be generated from experiment outputs.

---

# 34. Reproducibility

A clean environment should be able to reproduce the main experiment.

Create:

```text
requirements.txt
```

with pinned or bounded dependencies.

Recommended categories:

```text
numpy
pandas
geopandas
networkx
shapely
pyproj
scikit-learn
torch
torch-geometric          # if used
pulp
ortools                  # only if actually used
matplotlib
pyyaml
```

Only include packages actually required.

---

# 35. Main Reproduction Command

Create one entry point.

Preferred:

```bash
python run_pipeline.py --config config.yaml
```

It should execute:

```text
1. data audit
2. preprocessing
3. graph construction
4. STGNN training/loading
5. STGNN evaluation
6. travel-time inference
7. parcel feature generation
8. baseline optimization
9. proposed MILP optimization
10. ablation experiment
11. sensitivity analysis
12. tables
13. figures
14. reconciliation report
```

Allow stages to be skipped through CLI flags when appropriate.

---

# 36. Logging

Log all experiment settings.

Every run should store:

```text
timestamp
git commit hash if available
random seed
config
dataset fingerprints
solver
solver status
STGNN checkpoint
metrics
```

Save to:

```text
outputs/run_manifest.json
```

---

# 37. Tests

Create automated tests.

## Graph tests

Verify:

- CRS is correct;
- graph is non-empty;
- routing distances are non-negative;
- expected destination nodes are reachable.

## STGNN tests

Verify:

- forward pass shape;
- loss is finite;
- checkpoint reload works;
- predictions are finite;
- evaluation does not use training targets.

## MILP tests

Verify:

- every project is assigned exactly once;
- no parcel receives more than one project;
- CFE capacity is respected;
- hazard-excluded parcels are never selected;
- water-intensive projects respect water constraints.

## Reproducibility test

With the same seed and deterministic configuration:

```text
same inputs -> same deterministic MILP results
```

within reasonable neural-network tolerance.

---

# 38. Scientific Output Report

Generate:

```text
EXPERIMENT_REPORT.md
```

with:

## Data
What data were actually used?

## STGNN
Architecture and training configuration.

## Prediction results
Actual MAE and RMSE.

## Optimization
Actual solver and objective.

## Baselines
Exact definitions.

## Main results
Table generated from code.

## Ablation
Topology vs dynamic-STGNN contribution.

## Sensitivity
Actual observed response to weight changes.

## Limitations
Missing or synthetic data.

---

# 39. Manuscript Reconciliation Report

This file is mandatory:

```text
MANUSCRIPT_RECONCILIATION.md
```

Format:

```markdown
# Manuscript Reconciliation

## Statement requiring update

Paper:
"trained STGNN achieved MAE 1.84 min"

Repository result:
"MAE = 2.07 min"

Action:
Replace manuscript value with 2.07 min.

Reason:
Metric is now generated from held-out test data.
```

Do this for every discrepancy.

Especially inspect:

- MAE;
- RMSE;
- number of candidate parcels;
- source of parcels;
- number of CFE nodes;
- number of JMAS nodes;
- CFE capacities;
- project electrical loads;
- traffic data source;
- congestion factors;
- worker commute;
- environmental variables;
- Table 2;
- sensitivity-analysis values.

---

# 40. Manuscript Equations vs Implementation

Create a traceability table:

```text
outputs/equation_traceability.csv
```

Columns:

```text
equation
paper_section
description
implementation_file
function_or_class
verified
notes
```

At minimum trace:

```text
Eq. 1 graph definition
Eq. 2 node-layer union
Eq. 3 GCN
Eq. 4-7 GRU
Eq. 8 feature vector
Eq. 9 assignment variable
Eq. 10 objective
Eq. 11 single allocation
Eq. 12 plot capacity
Eq. 13 CFE capacity
Eq. 14 fault exclusion
Eq. 15 flood exclusion
Eq. 16 water stress
Eq. 17 STGNN travel-time inference
```

---

# 41. Code Quality

Requirements:

- no duplicated experimental logic;
- no magic numbers outside configuration;
- type hints where reasonable;
- meaningful docstrings;
- deterministic seeds;
- modular functions;
- explicit units;
- explicit CRS;
- no absolute Windows paths;
- no hidden manual post-processing.

Use `pathlib.Path`.

Example:

```python
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
```

Do not use:

```python
"D:\\some\\personal\\folder\\..."
```

---

# 42. README

Rewrite `README.md` so a reviewer can understand and reproduce the project.

Required sections:

```text
Title
Research objective
Architecture
Repository structure
Data sources
Observed vs synthetic data
Installation
Quick start
STGNN training
Optimization
Baselines
Reproduction of tables
Reproduction of figures
Expected output files
Limitations
Citation
```

Provide exact commands.

---

# 43. Important Terminology

Use consistently:

```text
siting
```

not:

```text
sitting
```

Use:

```text
Spatio-Temporal Graph Neural Network (STGNN)
Mixed-Integer Linear Programming (MILP)
```

If the mathematical model contains only linear terms and binary variables, prefer `MILP` rather than generic `MIP` when precision matters.

Use consistent spelling:

```text
Ciudad Juárez
San Jerónimo
JMAS
CFE
```

---

# 44. What Codex Must NOT Do

Codex must NOT:

1. hardcode manuscript results;
2. tune outputs simply to match Table 2;
3. fabricate STGNN training data;
4. call fixed congestion multipliers a trained neural network;
5. claim empirical parcels when random nodes are used;
6. invent utility capacities without labeling them as assumptions;
7. generate random hazard layers and describe them as official IMIP layers;
8. report test metrics calculated on training data;
9. use a random train/test split that leaks future traffic information;
10. silently change manuscript methodology;
11. silently change the meaning of variables;
12. suppress infeasibility;
13. modify results after optimization;
14. delete inconvenient experimental outputs;
15. claim reproducibility without a one-command pipeline.

---

# 45. Priority Order

Execute the work in this order.

## Priority 1 — Scientific integrity

- remove hardcoded outputs;
- audit empirical vs synthetic data;
- identify manuscript-code mismatches.

## Priority 2 — STGNN

- build real GCN-GRU;
- build temporal dataset;
- train;
- evaluate;
- save model;
- generate true MAE/RMSE.

## Priority 3 — MILP correctness

- fix shared CFE capacity aggregation;
- align project requirements;
- include worker commute if claimed;
- verify environmental constraints.

## Priority 4 — Experimental design

- implement fair baselines;
- implement Network-MILP ablation;
- regenerate Table 2;
- calculate improvements.

## Priority 5 — Sensitivity and reproducibility

- automate ±10%, ±20%, ±30%;
- save raw runs;
- produce figures;
- implement tests;
- document one-command reproduction.

## Priority 6 — Manuscript reconciliation

- compare every generated metric against the manuscript;
- list necessary manuscript edits.

---

# 46. Definition of Done

The repository is considered complete only when:

- [ ] No experimental result is manually overwritten.
- [ ] Every dataset is identified as empirical or synthetic.
- [ ] The real GCN-GRU implementation exists.
- [ ] STGNN training is reproducible.
- [ ] MAE and RMSE come from a held-out test set.
- [ ] Dynamic travel-time coefficients come from model inference.
- [ ] Every project is assigned exactly once.
- [ ] CFE capacity is aggregated at the substation level.
- [ ] Environmental constraints are enforced.
- [ ] Heavy Assembly parameters match the documented experiment.
- [ ] Worker commute is truly optimized if the manuscript claims it.
- [ ] GIS-AHP is actually AHP or is renamed appropriately.
- [ ] Euclidean MILP baseline exists.
- [ ] Network MILP ablation exists.
- [ ] STGNN-MILP proposed model exists.
- [ ] All methods use comparable feasibility constraints where scientifically appropriate.
- [ ] Table 2 is generated automatically.
- [ ] Sensitivity analysis is generated automatically.
- [ ] Figures are generated automatically.
- [ ] `requirements.txt` exists.
- [ ] `config.yaml` exists.
- [ ] `run_pipeline.py` exists.
- [ ] Tests pass.
- [ ] `DATA_AUDIT.md` exists.
- [ ] `REPOSITORY_AUDIT.md` exists.
- [ ] `EXPERIMENT_REPORT.md` exists.
- [ ] `MANUSCRIPT_RECONCILIATION.md` exists.
- [ ] `equation_traceability.csv` exists.
- [ ] README contains exact reproduction commands.

---

# 47. First Action for Codex

Do **not** immediately rewrite the repository.

First perform the audit.

Produce:

```text
REPOSITORY_AUDIT.md
DATA_AUDIT.md
IMPLEMENTATION_PLAN.md
```

Then begin correcting the code following the priorities above.

However, do not stop merely because the repository differs from the manuscript. Continue implementing everything that can be implemented from the available data.

Where information is missing:

```text
DO NOT GUESS.
DO NOT FABRICATE.
DOCUMENT THE GAP.
IMPLEMENT THE CORRECT INTERFACE.
```

---

# 48. Final Expected Deliverables

At the end, the repository should include enough evidence for an external reviewer to run:

```bash
pip install -r requirements.txt
python run_pipeline.py --config config.yaml
```

and obtain, without manual intervention:

```text
trained/evaluated STGNN
dynamic travel-time matrix
parcel feature matrix
baseline allocations
proposed allocation
Table 2
ablation results
sensitivity results
figures
experiment report
manuscript reconciliation report
```

The guiding principle for every decision is:

> **The code must determine the paper's numerical results; the paper's numerical results must never determine the code.**
