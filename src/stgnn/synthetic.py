"""Synthetic traffic scenario generation for reproducible STGNN experiments.

This module creates explicitly synthetic temporal traffic observations over the
empirical Ciudad Juarez road graph. It is intended for method validation only and
must not be described as observed historical traffic.
"""

from __future__ import annotations

import json
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd


BRIDGES = {
    "Zaragoza": (368423.7, 3504993.7),
    "Americas": (357900.5, 3510757.4),
    "Santa Teresa": (340439.2, 3515821.4),
}


@dataclass(frozen=True)
class SyntheticTrafficConfig:
    enabled: bool = True
    node_count: int = 64
    periods: int = 240
    frequency: str = "h"
    start_timestamp: str = "2026-01-01 00:00:00"
    base_speed_kph: float = 48.0
    noise_std_kph: float = 1.75
    output_dir: str = "outputs/synthetic"


def load_synthetic_config(config: dict[str, Any]) -> SyntheticTrafficConfig:
    synthetic = config.get("synthetic_traffic", {})
    if not isinstance(synthetic, dict):
        synthetic = {}
    return SyntheticTrafficConfig(
        enabled=bool(synthetic.get("enabled", SyntheticTrafficConfig.enabled)),
        node_count=int(synthetic.get("node_count", SyntheticTrafficConfig.node_count)),
        periods=int(synthetic.get("periods", SyntheticTrafficConfig.periods)),
        frequency=str(synthetic.get("frequency", SyntheticTrafficConfig.frequency)),
        start_timestamp=str(synthetic.get("start_timestamp", SyntheticTrafficConfig.start_timestamp)),
        base_speed_kph=float(synthetic.get("base_speed_kph", SyntheticTrafficConfig.base_speed_kph)),
        noise_std_kph=float(synthetic.get("noise_std_kph", SyntheticTrafficConfig.noise_std_kph)),
        output_dir=str(synthetic.get("output_dir", SyntheticTrafficConfig.output_dir)),
    )


def _read_vialidad(data_dir: Path) -> gpd.GeoDataFrame:
    zip_path = data_dir / "Vialidad.zip"
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(tmp)
        return gpd.read_file(Path(tmp) / "VialidadWgs84.shp")


def build_road_graph(data_dir: Path) -> nx.Graph:
    """Build the same major-road graph convention used by the POC simulator."""

    gdf_vial = _read_vialidad(data_dir)
    gdf_vial_main = gdf_vial[gdf_vial["V_PPAL"] == "SI"]
    graph = nx.Graph()
    for _, row in gdf_vial_main.iterrows():
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


def _select_sensor_nodes(graph: nx.Graph, node_count: int, seed: int) -> list[tuple[float, float]]:
    nodes = list(graph.nodes())
    rng = np.random.default_rng(seed)
    degree = dict(graph.degree())
    ranked = sorted(nodes, key=lambda node: degree[node], reverse=True)
    candidates = ranked[: max(node_count * 12, node_count)]
    selected: list[tuple[float, float]] = []
    for node in candidates:
        if all(np.linalg.norm(np.array(node) - np.array(other)) > 600.0 for other in selected):
            selected.append(node)
        if len(selected) == node_count:
            return selected
    remaining = [node for node in nodes if node not in selected]
    rng.shuffle(remaining)
    return selected + remaining[: node_count - len(selected)]


def _adjacency_for_nodes(graph: nx.Graph, nodes: list[tuple[float, float]]) -> np.ndarray:
    adjacency = np.zeros((len(nodes), len(nodes)), dtype="float32")
    index = {node: idx for idx, node in enumerate(nodes)}
    for node in nodes:
        src = index[node]
        lengths = nx.single_source_dijkstra_path_length(graph, node, cutoff=2200.0, weight="weight")
        nearest = sorted(
            ((distance, other) for other, distance in lengths.items() if other in index and other != node),
            key=lambda item: item[0],
        )[:4]
        for _, other in nearest:
            dst = index[other]
            adjacency[src, dst] = 1.0
            adjacency[dst, src] = 1.0
    return adjacency


def _bridge_proximity(node: tuple[float, float], bridge_xy: tuple[float, float]) -> float:
    distance_m = np.linalg.norm(np.array(node) - np.array(bridge_xy))
    return float(np.exp(-distance_m / 8500.0))


def generate_synthetic_traffic(
    repo_root: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Generate synthetic traffic CSV, adjacency matrix, and metadata."""

    seed = int(config.get("random_seed", 42))
    synthetic_config = load_synthetic_config(config)
    data_dir = repo_root / config.get("paths", {}).get("data_dir", "Datos")
    output_dir = repo_root / synthetic_config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    graph = build_road_graph(data_dir)
    nodes = _select_sensor_nodes(graph, synthetic_config.node_count, seed)
    adjacency = _adjacency_for_nodes(graph, nodes)
    timestamps = pd.date_range(
        synthetic_config.start_timestamp,
        periods=synthetic_config.periods,
        freq=synthetic_config.frequency,
    )
    rng = np.random.default_rng(seed)
    rows = []
    for node_idx, node in enumerate(nodes):
        bridge_pressure = max(_bridge_proximity(node, bridge_xy) for bridge_xy in BRIDGES.values())
        local_phase = rng.uniform(0, 2 * np.pi)
        for time_idx, timestamp in enumerate(timestamps):
            hour = timestamp.hour + timestamp.minute / 60.0
            morning_peak = np.exp(-((hour - 7.5) ** 2) / 5.0)
            evening_peak = np.exp(-((hour - 17.5) ** 2) / 6.0)
            daily_wave = 2.0 * np.sin((2 * np.pi * time_idx / 24.0) + local_phase)
            weekly_wave = 1.25 * np.sin(2 * np.pi * time_idx / (24.0 * 7.0))
            congestion = bridge_pressure * (10.0 * morning_peak + 13.0 * evening_peak)
            speed = synthetic_config.base_speed_kph + daily_wave + weekly_wave - congestion
            speed += rng.normal(0.0, synthetic_config.noise_std_kph)
            speed = float(np.clip(speed, 12.0, 70.0))
            segment_length_km = 0.45 + 0.55 * bridge_pressure + 0.15 * (node_idx % 5)
            travel_time_min = float((segment_length_km / speed) * 60.0)
            rows.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "road_segment_id": f"synthetic_segment_{node_idx:03d}",
                    "speed_kph": speed,
                    "travel_time_min": travel_time_min,
                    "utm_easting": float(node[0]),
                    "utm_northing": float(node[1]),
                    "synthetic": True,
                }
            )

    traffic_path = output_dir / "synthetic_traffic.csv"
    adjacency_path = output_dir / "synthetic_adjacency.npy"
    metadata_path = output_dir / "synthetic_traffic_metadata.json"
    pd.DataFrame(rows).to_csv(traffic_path, index=False)
    np.save(adjacency_path, adjacency)
    metadata = {
        "status": "generated",
        "scenario": "synthetic_traffic_over_empirical_road_graph",
        "observed_historical_traffic": False,
        "road_graph_nodes": graph.number_of_nodes(),
        "road_graph_edges": graph.number_of_edges(),
        "synthetic_sensor_nodes": len(nodes),
        "periods": synthetic_config.periods,
        "frequency": synthetic_config.frequency,
        "traffic_csv": str(traffic_path),
        "adjacency_npy": str(adjacency_path),
        "columns": ["timestamp", "road_segment_id", "speed_kph", "travel_time_min"],
    }
    with open(metadata_path, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    return metadata


def generate_synthetic_travel_time_matrix(repo_root: Path, config: dict[str, Any]) -> Path:
    """Create a synthetic parcel-to-border travel-time matrix for MILP coefficients."""

    outputs_dir = repo_root / config.get("paths", {}).get("outputs_dir", "outputs") / "metrics"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(int(config.get("random_seed", 42)))
    zone_by_parcel = (
        ["San Jeronimo"] * 10
        + ["Norte Centro"] * 10
        + ["Oriente"] * 10
        + ["Sur"] * 10
        + ["Suroriente"] * 10
    )
    zone_base_minutes = {
        "San Jeronimo": {"Santa Teresa": 7.0, "Americas": 24.0, "Zaragoza": 31.0},
        "Norte Centro": {"Santa Teresa": 24.0, "Americas": 9.0, "Zaragoza": 22.0},
        "Oriente": {"Santa Teresa": 34.0, "Americas": 23.0, "Zaragoza": 10.0},
        "Sur": {"Santa Teresa": 30.0, "Americas": 20.0, "Zaragoza": 18.0},
        "Suroriente": {"Santa Teresa": 38.0, "Americas": 28.0, "Zaragoza": 17.0},
    }
    peak_factor = {"Santa Teresa": 1.10, "Americas": 1.75, "Zaragoza": 1.55}
    rows = []
    for parcel_id, zone in enumerate(zone_by_parcel):
        parcel_noise = rng.normal(0.0, 0.75)
        for bridge in BRIDGES:
            baseline = zone_base_minutes[zone][bridge] + parcel_noise
            predicted = max(3.0, baseline * peak_factor[bridge] + rng.normal(0.0, 0.5))
            rows.append(
                {
                    "parcel_id": parcel_id,
                    "border_crossing": bridge,
                    "timestamp_or_scenario": "synthetic_peak_shift",
                    "predicted_minutes": round(float(predicted), 4),
                    "baseline_minutes": round(float(baseline), 4),
                    "source": "synthetic_scenario_not_observed_traffic",
                }
            )
    matrix_path = outputs_dir / "travel_time_matrix.csv"
    pd.DataFrame(rows).to_csv(matrix_path, index=False)
    return matrix_path
