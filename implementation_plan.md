# Hybrid GNN-MIP Siting Simulation Plan

This plan details the implementation of a Python simulation that replicates the Spatio-Temporal Graph Neural Network (STGNN) and Mixed-Integer Programming (MIP) hybrid facility location model for Ciudad Juárez, Chihuahua, as described in [Art_V03.pdf](file:///C:/Users/alann/Desktop/MIAAD/MICAI_2026/Microsoft+Word+Proceedings+Template+ZIP/Art_V03.pdf). 

## Goal Description

The objetivo is to create a fully functional Python pipeline that uses real geographic layers of Ciudad Juárez to optimize the siting of 15 new industrial facilities across 50 candidate plots, comparing the Proposed GNN-MIP model against two baselines:
1.  **Static GIS-AHP (Baseline 1)**: Greedy allocation based on straight-line Euclidean distance overlays, ignoring joint capacity constraints and network topologies.
2.  **Abstract MILP (Baseline 2)**: Mathematical optimization model solved under hard bounds but using flat Euclidean distances, ignoring street networks, traffic congestion, and hazard barriers.
3.  **Proposed GNN-MIP**: Optimization model using non-Euclidean network distances, dynamic travel times (simulating STGNN predictions with peak hour congestion), and hard environmental constraints.

The simulation will ingest spatial shapefiles from [Datos/](file:///c:/Users/alann/Desktop/MIAAD/MICAI_2026/POC_SIMULATION/Datos), solve the models, write results to `siting-results.csv`, and plot the final spatial layout in `siting-comparison.png` (matching the layout in the paper).

---

## User Review Required

> [!IMPORTANT]
> - **Candidate Plots and Infrastructure Nodes**: Since there is no explicit separate file containing the 50 candidate vacant parcels, we will select 50 candidate plots from the vacant polygons in [Traza_Wgs84.shp](file:///c:/Users/alann/Desktop/MIAAD/MICAI_2026/POC_SIMULATION/Datos/Traza.zip) and from existing industrial clusters. We will extract 5 CFE substations and 5 JMAS sewer outlets from the utilities in [denue_inegi_08_.csv](file:///c:/Users/alann/Desktop/MIAAD/MICAI_2026/POC_SIMULATION/Datos/denue_08_csv.zip) (activity code starting with 22).
> - **Spatio-Temporal GNN Emulation**: To capture the dynamic, non-Euclidean nature of logistics times without needing a long Deep Learning training phase, we will implement a Python class representing a GCN-GRU. It will compute shortest path network distances on the major road network of Ciudad Juárez (`V_PPAL == 'SI'` from [VialidadWgs84.shp](file:///c:/Users/alann/Desktop/MIAAD/MICAI_2026/POC_SIMULATION/Datos/Vialidad.zip)) and apply time-of-day traffic congestion multipliers (e.g., 1.5x congestion factor during peak commuting shifts towards international bridges) to generate the dynamic travel time matrix $T_{jk}(t)$.

---

## Proposed Changes

We will create two new files in the workspace:

### [Simulation Pipeline]

#### [NEW] [simulate_siting.py](file:///c:/Users/alann/Desktop/MIAAD/MICAI_2026/POC_SIMULATION/simulate_siting.py)
This is the core Python script. It will:
1.  **Extract and Load Spatial Data**: Unzip and load shapefiles/CSVs (`Vialidad`, `Colonias`, `Traza`, `AreasVerdes`, `denue_08`).
2.  **Filter and Build Graph**: Filter the road network to keep primary streets (`V_PPAL == "SI"`) and build a NetworkX graph with UTM coordinates.
3.  **Define Entities**:
    *   Set the 3 border ports of entry: Zaragoza, Américas, Jerónimo-Santa Teresa.
    *   Identify CFE and JMAS infrastructure nodes from the DENUE utilities dataset.
    *   Select 50 candidate vacant plots distributed across the 5 municipal planning zones (Norte Centro, Oriente, Sur, Suroriente, and San Jerónimo).
4.  **Emulate GNN Travel Times**: Run network shortest path queries and apply congestion factors to get dynamic travel times.
5.  **Evaluate Utilities and Hazards**:
    *   Calculate network distance to nearest CFE substation and JMAS sewer collector.
    *   Synthesize hazard risk layers (geological faults, flood susceptibility, water stress) based on topographic properties.
6.  **Formulate and Solve optimization (PuLP)**:
    *   Solve the **Static GIS-AHP** model.
    *   Solve the **Abstract MILP** model.
    *   Solve the **Proposed GNN-MIP** model.
7.  **Generate Outputs**: Save the metrics comparison to a text report, output the spatial allocation details to `siting-results.csv`, and render the final comparison plot to `siting-comparison.png`.

#### [NEW] [run_simulation.bat](file:///c:/Users/alann/Desktop/MIAAD/MICAI_2026/POC_SIMULATION/run_simulation.bat)
A simple Windows command script to execute the simulation.

---

## Verification Plan

### Automated Tests
*   Run the simulation script via batch command:
    ```powershell
    python simulate_siting.py
    ```
*   Verify that `siting-results.csv` and `siting-comparison.png` are created and contain non-empty data.
*   Compare the output metrics with Table 2 of the paper:
    *   *CFE grid extension* should decrease from ~40.8 km (baselines) to ~36.6 km (GNN-MIP).
    *   *JMAS sewer extension* should decrease from ~44.8 km to ~39.5 km.
    *   *Average commute time* should decrease from ~24-27 min to ~17.6 min.
    *   *Substation overloads and hazard violations* should drop to 0 for the GNN-MIP model.

### Manual Verification
*   Inspect the generated `siting-comparison.png` image to ensure that the layout matches the visual arrangement and color coding shown in the paper's results.
