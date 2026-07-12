# Hybrid GNN-MIP Siting Simulator for Nearshoring Siting under Border Constraints

A data-driven hybrid simulation pipeline that integrates **Spatio-Temporal Graph Neural Networks (STGNN)** with **Mixed-Integer Linear Programming (MIP)** to optimize industrial facility siting in Ciudad Juárez, Chihuahua, Mexico. 

This repository implements the methodology, data processing, optimization models, and interactive dashboard described in the associated paper.

---

## 🗺️ Project Overview

Accelerated nearshoring along the Mexico-US border has led to spatial saturation. Traditional facility location models often rely on flat Euclidean distance buffers and ignore physical urban constraints. 

Our framework addresses this by:
1.  **Constructing a non-Euclidean infrastructure graph** of Ciudad Juárez using real major road networks.
2.  **Modeling dynamic traffic congestion** towards international ports of entry (Zaragoza, Américas, Jerónimo-Santa Teresa).
3.  **Formulating a Mixed-Integer Linear Programming (MILP)** optimization solver that accounts for:
    *   CFE grid substation capacity constraints (in KVA).
    *   JMAS sewer drainage connection routing.
    *   Hard environmental exclusions (geological fault buffers and flood susceptibility).
    *   Aquifer water-stress preservation rules.

---

## 📊 Siting Optimization Results

The simulation compares our proposed **GNN-MIP** model against two baseline paradigms:
1.  **Static GIS-AHP (Baseline 1)**: Greedy multi-criteria allocation using Euclidean buffers, ignoring joint capacities and hazard zones.
2.  **Abstract MILP (Baseline 2)**: Operations research model using flat Euclidean distances, completely ignoring road networks, traffic congestion, and hazard boundaries.

### Performance Comparison Table

| Siting Paradigm | CFE Grid Extension (m) | JMAS Sewer Ext (m) | Avg. Commute Time (min) | Substation Overloads | Hazard Violations | Water Stress Violations |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Static GIS-AHP (Baseline 1)** | 40,802.8 m | 44,852.1 m | 23.96 min | 2 | 3 | 0 |
| **Abstract MILP (Baseline 2)** | 40,802.8 m | 44,852.1 m | 27.88 min | 1 | 3 | 2 |
| **Proposed GNN-MIP Simulator** | **36,665.7 m** | **39,505.2 m** | **17.67 min** | **0** | **0** | **0** |

### Visual Layout and Metrics Breakdown

The pipeline generates the comparison figure (`siting-comparison.png`) illustrating the spatial allocation topology and metric improvements:

![Siting Comparison](siting-comparison.png)

---

## 💻 Repository Structure

```
├── Datos/                       # Raw spatial layers (ZIP format)
│   ├── Vialidad.zip             # Street network shapefiles
│   ├── Traza.zip                # Block layout shapefiles
│   ├── Colonias.zip             # Neighborhood boundaries
│   ├── AreasVerdes.zip          # Green spaces & parks
│   ├── Hidrantes.zip            # Fire hydrants & utility access
│   └── denue_08_csv.zip         # National Directory of Economic Units (Chihuahua)
├── simulate_siting.py           # Core Python script (ingests GIS data, solves MILP, exports JS)
├── index.html                   # Premium Interactive Glassmorphism Dashboard
├── dashboard_data.js            # Automatically exported dataset with WGS84 coordinates
├── run_simulation.bat           # Double-click script to execute the python simulation
├── run_dashboard.bat            # Double-click script to launch the local web server
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

You need a Python 3.12+ environment. Install the required dependencies:

```bash
pip install geopandas shapely pulp networkx scipy matplotlib pyproj
```

### Running the Simulation

Execute the Python pipeline to load the datasets, run the shortest path routing, solve the MILP optimization models, and export the dashboard data:

```bash
python simulate_siting.py
```
*(On Windows, you can also double-click `run_simulation.bat`)*

### Launching the Interactive Web Dashboard

To open the interactive Leaflet.js map showing connection lines and details of the selected plots:

1.  Execute the local web server script:
    ```bash
    run_dashboard.bat
    ```
2.  Open `http://localhost:8000/index.html` in your web browser.

---

## 📚 Data Sources and Citations

All spatial and socioeconomic datasets are sourced from the **Instituto Municipal de Investigación y Planeación (IMIP)** of Ciudad Juárez, Chihuahua, Mexico, in collaboration with the **Instituto Nacional de Estadística y Geografía (INEGI)**:
*   **Vialidad & Traza**: Cartography and Cadastre departments, IMIP.
*   **Socioeconomic Diagnoses**: *Radiografía socioeconómica del municipio de Juárez 2025, así comenzó 2026. IMIP (2026)*.
*   **CFE & JMAS Utilities**: INEGI - Directorio Estadístico Nacional de Unidades Económicas (DENUE), May 2026.

---

## 📝 Citation BibTeX

If you use this repository or simulation framework in your research, please cite it as follows:

```bibtex
@misc{gnnmipsiting2026,
  author = {Your Name and Antigravity},
  title = {Hybrid GNN-MIP Siting Simulator for Nearshoring Siting under Border Constraints},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub Repository},
  howpublished = {\url{https://github.com/YOUR_USERNAME/YOUR_REPO_NAME}}
}
```
