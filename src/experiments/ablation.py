"""Fair MILP ablation study for the synthetic STGNN scenario.

The ablation compares three optimization variants with the same project set,
candidate parcels, synthetic CFE capacity constraints, synthetic hazards, and
water-stress eligibility masks:

1. Euclidean MILP: Euclidean utility and border travel-time coefficients.
2. Network MILP: network utility and free-flow border travel-time coefficients.
3. Synthetic-STGNN MILP: network utility and synthetic dynamic travel-time matrix.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
import pulp
from scipy.spatial import KDTree


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    profile: str
    load_kva: float
    freight_weight: float
    heavy_water: bool


def _read_yaml(path: Path) -> dict:
    try:
        import yaml

        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except ImportError:
        from src.stgnn.train import _load_simple_yaml

        return _load_simple_yaml(path)


def _load_layers(data_dir: Path):
    with tempfile.TemporaryDirectory() as tmp:
        for filename in ["Vialidad.zip", "Colonias.zip"]:
            with zipfile.ZipFile(data_dir / filename, "r") as archive:
                archive.extractall(tmp)
        return (
            gpd.read_file(Path(tmp) / "VialidadWgs84.shp"),
            gpd.read_file(Path(tmp) / "ColoniasWgs84.shp"),
        )


def _build_graph(gdf_vial: gpd.GeoDataFrame) -> nx.Graph:
    graph = nx.Graph()
    for _, row in gdf_vial[gdf_vial["V_PPAL"] == "SI"].iterrows():
        geom = row.geometry
        if geom is None:
            continue
        lines = [geom] if geom.geom_type == "LineString" else list(getattr(geom, "geoms", []))
        for line in lines:
            coords = list(line.coords)
            for idx in range(len(coords) - 1):
                p1 = coords[idx]
                p2 = coords[idx + 1]
                distance = float(np.linalg.norm(np.array(p1) - np.array(p2)))
                graph.add_edge(p1, p2, weight=distance)
    largest_cc = max(nx.connected_components(graph), key=len)
    return graph.subgraph(largest_cc).copy()


def _distance_to_fault(x: float, y: float) -> float:
    p1 = np.array([355000.0, 3512000.0])
    p2 = np.array([368000.0, 3501000.0])
    p3 = np.array([x, y])
    line = p2 - p1
    point = p1 - p3
    cross_2d = line[0] * point[1] - line[1] * point[0]
    return float(np.abs(cross_2d) / np.linalg.norm(line))


def build_scenario(repo_root: Path, config: dict) -> dict:
    data_dir = repo_root / config.get("paths", {}).get("data_dir", "Datos")
    gdf_vial, gdf_col = _load_layers(data_dir)
    graph = _build_graph(gdf_vial)
    node_coords = list(graph.nodes())
    node_array = np.array(node_coords)
    kdtree = KDTree(node_array)

    def snap_to_graph(x: float, y: float):
        _, idx = kdtree.query([x, y])
        return node_coords[idx]

    zones = {
        "San Jeronimo": {"center": (340000.0, 3512000.0)},
        "Norte Centro": {"center": (357500.0, 3509500.0)},
        "Oriente": {"center": (365500.0, 3503500.0)},
        "Sur": {"center": (358500.0, 3497500.0)},
        "Suroriente": {"center": (367500.0, 3493500.0)},
    }
    bridges = {
        "Zaragoza": {"coords": snap_to_graph(368423.7, 3504993.7)},
        "Americas": {"coords": snap_to_graph(357900.5, 3510757.4)},
        "Santa Teresa": {"coords": snap_to_graph(340439.2, 3515821.4)},
    }
    cfe_substations = {
        name: {"coords": snap_to_graph(info["center"][0], info["center"][1]), "capacity": 5000.0}
        for name, info in zones.items()
    }
    jmas_outlets = {
        name: {"coords": snap_to_graph(info["center"][0] - 500.0, info["center"][1] - 500.0)}
        for name, info in zones.items()
    }

    rng = np.random.default_rng(int(config.get("random_seed", 42)))
    flood_basin_1 = np.array([358000.0, 3511000.0])
    flood_basin_2 = np.array([367000.0, 3504500.0])
    base_price = {
        "San Jeronimo": 110000.0,
        "Norte Centro": 280000.0,
        "Oriente": 220000.0,
        "Sur": 160000.0,
        "Suroriente": 130000.0,
    }
    water_stress = {
        "San Jeronimo": 1,
        "Norte Centro": 2,
        "Oriente": 2,
        "Sur": 4,
        "Suroriente": 4,
    }
    candidate_plots = []
    plot_id = 0
    for zone_name, info in zones.items():
        cx, cy = info["center"]
        zone_nodes = [node for node in graph.nodes() if np.linalg.norm(np.array(node) - np.array([cx, cy])) < 4500.0]
        if len(zone_nodes) < 10:
            zone_nodes = sorted(graph.nodes(), key=lambda node: np.linalg.norm(np.array(node) - np.array([cx, cy])))[:100]
        selected = []
        for idx in rng.choice(len(zone_nodes), size=min(len(zone_nodes), 50), replace=False):
            node = zone_nodes[idx]
            if all(np.linalg.norm(np.array(node) - np.array(other)) > 300.0 for other in selected):
                selected.append(node)
            if len(selected) == 10:
                break
        if len(selected) < 10:
            selected = zone_nodes[:10]
        for node in selected:
            x, y = node
            fault = int(_distance_to_fault(x, y) < 600.0)
            flood = int(
                np.linalg.norm(np.array([x, y]) - flood_basin_1) < 700.0
                or np.linalg.norm(np.array([x, y]) - flood_basin_2) < 700.0
            )
            price_multiplier = 0.8 if fault or flood else 1.0
            candidate_plots.append(
                {
                    "id": plot_id,
                    "coords": node,
                    "zone": zone_name,
                    "price": base_price[zone_name] * price_multiplier * rng.uniform(0.9, 1.1),
                    "water_stress": water_stress[zone_name],
                    "fault_hazard": fault,
                    "flood_hazard": flood,
                }
            )
            plot_id += 1

    colonia_centroids = [snap_to_graph(geom.centroid.x, geom.centroid.y) for geom in gdf_col.geometry if geom is not None]
    col_tree = KDTree(np.array(colonia_centroids))
    distances = {
        "cfe_network": {},
        "cfe_euclidean": {},
        "jmas_network": {},
        "jmas_euclidean": {},
        "bridge_network": {},
        "bridge_euclidean": {},
        "commute": {},
    }
    free_flow_m_per_min = 50.0 * 1000.0 / 60.0
    commute_m_per_min = 40.0 * 1000.0 / 60.0
    for plot in candidate_plots:
        pid = plot["id"]
        coords = plot["coords"]
        for key in ["cfe_network", "cfe_euclidean", "jmas_network", "jmas_euclidean", "bridge_network", "bridge_euclidean"]:
            distances[key][pid] = {}
        for zone_name, cfe in cfe_substations.items():
            cfe_coords = cfe["coords"]
            distances["cfe_network"][pid][zone_name] = nx.shortest_path_length(graph, coords, cfe_coords, weight="weight")
            distances["cfe_euclidean"][pid][zone_name] = float(np.linalg.norm(np.array(coords) - np.array(cfe_coords)))
        for zone_name, jmas in jmas_outlets.items():
            jmas_coords = jmas["coords"]
            distances["jmas_network"][pid][zone_name] = nx.shortest_path_length(graph, coords, jmas_coords, weight="weight")
            distances["jmas_euclidean"][pid][zone_name] = float(np.linalg.norm(np.array(coords) - np.array(jmas_coords)))
        for bridge_name, bridge in bridges.items():
            bridge_coords = bridge["coords"]
            network_distance = nx.shortest_path_length(graph, coords, bridge_coords, weight="weight")
            euclidean_distance = float(np.linalg.norm(np.array(coords) - np.array(bridge_coords)))
            distances["bridge_network"][pid][bridge_name] = network_distance / free_flow_m_per_min
            distances["bridge_euclidean"][pid][bridge_name] = euclidean_distance / free_flow_m_per_min
        _, idxs = col_tree.query(coords, k=10)
        commute_times = []
        for idx in idxs:
            col_coords = colonia_centroids[idx]
            commute_times.append(nx.shortest_path_length(graph, coords, col_coords, weight="weight") / commute_m_per_min)
        distances["commute"][pid] = float(np.mean(commute_times))

    dynamic_matrix_path = repo_root / config.get("paths", {}).get("outputs_dir", "outputs") / "metrics" / "travel_time_matrix.csv"
    dynamic_travel = {}
    if dynamic_matrix_path.exists():
        for _, row in pd.read_csv(dynamic_matrix_path).iterrows():
            dynamic_travel[(int(row["parcel_id"]), row["border_crossing"])] = float(row["predicted_minutes"])

    projects = [
        *[Project(i, f"Heavy_{i}", "Heavy", 1000.0, 1.5, True) for i in range(1, 6)],
        *[Project(i, f"Logistics_{i}", "Logistics", 100.0, 5.0, False) for i in range(6, 11)],
        *[Project(i, f"LightMfg_{i}", "LightMfg", 200.0, 1.0, False) for i in range(11, 16)],
    ]
    return {
        "zones": zones,
        "bridges": bridges,
        "candidate_plots": candidate_plots,
        "projects": projects,
        "distances": distances,
        "cfe_substations": cfe_substations,
        "dynamic_travel": dynamic_travel,
    }


def _nearest_zone(distance_map: dict, plot_id: int) -> str:
    return min(distance_map[plot_id], key=lambda zone: distance_map[plot_id][zone])


def solve_variant(scenario: dict, variant: dict, weights: dict) -> tuple[dict, dict]:
    plots = scenario["candidate_plots"]
    projects = scenario["projects"]
    distances = scenario["distances"]
    zones = scenario["zones"]
    bridges = scenario["bridges"]
    cfe_substations = scenario["cfe_substations"]
    dynamic_travel = scenario["dynamic_travel"]
    cfe_key = variant["cfe_distance"]
    jmas_key = variant["jmas_distance"]
    bridge_key = variant["bridge_distance"]
    model = pulp.LpProblem(f"{variant['id']}_siting", pulp.LpMinimize)
    z = pulp.LpVariable.dicts("z", ((plot["id"], project.id) for plot in plots for project in projects), cat="Binary")

    objective_terms = []
    for plot in plots:
        pid = plot["id"]
        nearest_cfe = min(distances[cfe_key][pid].values())
        nearest_jmas = min(distances[jmas_key][pid].values())
        for project in projects:
            bridge_cost = 0.0
            for bridge_name in bridges:
                if variant["dynamic_stgnn"]:
                    bridge_minutes = dynamic_travel.get((pid, bridge_name), distances["bridge_network"][pid][bridge_name])
                else:
                    bridge_minutes = distances[bridge_key][pid][bridge_name]
                bridge_cost += bridge_minutes * project.freight_weight
            worker_commute_cost = (
                weights.get("delta_worker_commute", 0.0) * distances["commute"][pid]
                if project.profile == "LightMfg"
                else 0.0
            )
            total = (
                plot["price"]
                + weights["alpha"] * nearest_cfe
                + weights["beta"] * nearest_jmas
                + weights["gamma"] * bridge_cost
                + worker_commute_cost
            )
            objective_terms.append(z[(pid, project.id)] * total)
    model += pulp.lpSum(objective_terms)

    for project in projects:
        model += pulp.lpSum(z[(plot["id"], project.id)] for plot in plots) == 1
    for plot in plots:
        model += pulp.lpSum(z[(plot["id"], project.id)] for project in projects) <= 1

    cfe_groups = {zone: [] for zone in zones}
    for plot in plots:
        cfe_groups[_nearest_zone(distances[cfe_key], plot["id"])].append(plot["id"])
    for zone_name, plot_ids in cfe_groups.items():
        model += (
            pulp.lpSum(z[(pid, project.id)] * project.load_kva for pid in plot_ids for project in projects)
            <= cfe_substations[zone_name]["capacity"]
        )

    for plot in plots:
        if plot["fault_hazard"] or plot["flood_hazard"]:
            for project in projects:
                model += z[(plot["id"], project.id)] == 0
        if plot["water_stress"] >= 3:
            for project in projects:
                if project.heavy_water:
                    model += z[(plot["id"], project.id)] == 0

    start = time.perf_counter()
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    runtime = time.perf_counter() - start
    allocation = {}
    for project in projects:
        for plot in plots:
            value = pulp.value(z[(plot["id"], project.id)])
            if value is not None and value > 0.5:
                allocation[project.id] = plot["id"]
    metrics = evaluate_allocation(scenario, allocation, variant["id"])
    metrics.update(
        {
            "model": variant["name"],
            "solver_status": pulp.LpStatus[model.status],
            "objective_value": float(pulp.value(model.objective)) if pulp.value(model.objective) is not None else None,
            "solver_runtime_sec": runtime,
            "network_topology": variant["network_topology"],
            "dynamic_stgnn": variant["dynamic_stgnn"],
            "cfe_capacity": True,
            "environmental_constraints": True,
        }
    )
    return allocation, metrics


def evaluate_allocation(scenario: dict, allocation: dict[int, int], variant_id: str) -> dict:
    plots_by_id = {plot["id"]: plot for plot in scenario["candidate_plots"]}
    projects_by_id = {project.id: project for project in scenario["projects"]}
    distances = scenario["distances"]
    substation_loads = {zone: 0.0 for zone in scenario["zones"]}
    cfe_ext = 0.0
    jmas_ext = 0.0
    commute = []
    profile3_commute = []
    hazards = 0
    water = 0
    freeflow_border_times = []
    dynamic_border_times = []
    for project_id, plot_id in allocation.items():
        plot = plots_by_id[plot_id]
        project = projects_by_id[project_id]
        cfe_zone = _nearest_zone(distances["cfe_network"], plot_id)
        jmas_zone = _nearest_zone(distances["jmas_network"], plot_id)
        cfe_ext += distances["cfe_network"][plot_id][cfe_zone]
        jmas_ext += distances["jmas_network"][plot_id][jmas_zone]
        substation_loads[cfe_zone] += project.load_kva
        commute.append(distances["commute"][plot_id])
        if project.profile == "LightMfg":
            profile3_commute.append(distances["commute"][plot_id])
        freeflow_border_times.append(
            np.mean([distances["bridge_network"][plot_id][bridge] for bridge in scenario["bridges"]])
        )
        dynamic_border_times.append(
            np.mean(
                [
                    scenario["dynamic_travel"].get((plot_id, bridge), distances["bridge_network"][plot_id][bridge])
                    for bridge in scenario["bridges"]
                ]
            )
        )
        hazards += int(plot["fault_hazard"] or plot["flood_hazard"])
        water += int(project.heavy_water and plot["water_stress"] >= 3)
    overloads = sum(
        1
        for zone, load in substation_loads.items()
        if load > scenario["cfe_substations"][zone]["capacity"]
    )
    return {
        "variant_id": variant_id,
        "cfe_ext": cfe_ext,
        "jmas_ext": jmas_ext,
        "avg_commute": float(np.mean(commute)) if commute else np.nan,
        "profile3_avg_commute": float(np.mean(profile3_commute)) if profile3_commute else np.nan,
        "mean_freeflow_border_time": float(np.mean(freeflow_border_times)) if freeflow_border_times else np.nan,
        "mean_dynamic_border_time": float(np.mean(dynamic_border_times)) if dynamic_border_times else np.nan,
        "overloads": overloads,
        "hazards": hazards,
        "water": water,
        "assigned_projects": len(allocation),
    }


def write_markdown_table(frame: pd.DataFrame, path: Path) -> None:
    lines = [
        "| " + " | ".join(frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_ablation(config_path: Path) -> pd.DataFrame:
    repo_root = config_path.resolve().parent
    config = _read_yaml(config_path)
    scenario = build_scenario(repo_root, config)
    weights = {
        "alpha": float(config.get("optimization", {}).get("alpha_cfe_distance", 1.0)),
        "beta": float(config.get("optimization", {}).get("beta_jmas_distance", 1.0)),
        "gamma": float(config.get("optimization", {}).get("gamma_bridge_travel", 2.0)),
        "delta_worker_commute": float(config.get("optimization", {}).get("delta_worker_commute_profile3", 0.0)),
    }
    variants = [
        {
            "id": "euclidean_milp",
            "name": "Euclidean MILP",
            "cfe_distance": "cfe_euclidean",
            "jmas_distance": "jmas_euclidean",
            "bridge_distance": "bridge_euclidean",
            "network_topology": False,
            "dynamic_stgnn": False,
        },
        {
            "id": "network_milp",
            "name": "Network MILP",
            "cfe_distance": "cfe_network",
            "jmas_distance": "jmas_network",
            "bridge_distance": "bridge_network",
            "network_topology": True,
            "dynamic_stgnn": False,
        },
        {
            "id": "synthetic_stgnn_milp",
            "name": "Synthetic-STGNN MILP",
            "cfe_distance": "cfe_network",
            "jmas_distance": "jmas_network",
            "bridge_distance": "bridge_network",
            "network_topology": True,
            "dynamic_stgnn": True,
        },
    ]
    metrics = []
    allocations = []
    allocation_by_variant = {}
    for variant in variants:
        allocation, row = solve_variant(scenario, variant, weights)
        allocation_by_variant[variant["id"]] = allocation
        metrics.append(row)
        for project_id, plot_id in allocation.items():
            allocations.append({"variant_id": variant["id"], "project_id": project_id, "plot_id": plot_id})

    euclidean_allocation = allocation_by_variant["euclidean_milp"]
    network_allocation = allocation_by_variant["network_milp"]
    for row in metrics:
        variant_allocation = allocation_by_variant[row["variant_id"]]
        row["selected_plot_set"] = ";".join(str(plot_id) for plot_id in sorted(variant_allocation.values()))
        row["assignment_changes_vs_euclidean"] = sum(
            1 for project_id, plot_id in variant_allocation.items() if euclidean_allocation.get(project_id) != plot_id
        )
        row["assignment_changes_vs_network"] = sum(
            1 for project_id, plot_id in variant_allocation.items() if network_allocation.get(project_id) != plot_id
        )

    outputs_dir = repo_root / config.get("paths", {}).get("outputs_dir", "outputs")
    metrics_dir = outputs_dir / "metrics"
    tables_dir = outputs_dir / "tables"
    allocations_dir = outputs_dir / "allocations"
    for directory in [metrics_dir, tables_dir, allocations_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    metrics_frame = pd.DataFrame(metrics)
    metrics_frame.to_csv(metrics_dir / "ablation_results.csv", index=False)
    pd.DataFrame(allocations).to_csv(allocations_dir / "ablation_allocations.csv", index=False)
    table_frame = metrics_frame[
        [
            "model",
            "network_topology",
            "dynamic_stgnn",
            "cfe_capacity",
            "environmental_constraints",
            "cfe_ext",
            "jmas_ext",
            "avg_commute",
            "profile3_avg_commute",
            "mean_freeflow_border_time",
            "mean_dynamic_border_time",
            "overloads",
            "hazards",
            "water",
            "objective_value",
            "assignment_changes_vs_euclidean",
            "assignment_changes_vs_network",
        ]
    ].copy()
    table_frame.to_csv(tables_dir / "ablation_summary.csv", index=False)
    write_markdown_table(table_frame.round(4), tables_dir / "ablation_summary.md")
    manifest = {
        "scenario": "synthetic_ablation_over_empirical_road_graph",
        "observed_historical_traffic": False,
        "variants": variants,
        "weights": weights,
    }
    (metrics_dir / "ablation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return metrics_frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fair MILP ablation study.")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    frame = run_ablation(Path(args.config))
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
