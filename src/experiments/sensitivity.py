"""Sensitivity analysis for objective weights in the synthetic STGNN MILP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .ablation import _read_yaml, build_scenario, solve_variant, write_markdown_table


PROPOSED_VARIANT = {
    "id": "synthetic_stgnn_milp",
    "name": "Synthetic-STGNN MILP",
    "cfe_distance": "cfe_network",
    "jmas_distance": "jmas_network",
    "bridge_distance": "bridge_network",
    "network_topology": True,
    "dynamic_stgnn": True,
}


def _variations_from_config(config: dict) -> list[float]:
    configured = config.get("sensitivity", {}).get("variations", [-0.30, -0.20, -0.10, 0.0, 0.10, 0.20, 0.30])
    return [float(value) for value in configured]


def _base_weights(config: dict) -> dict[str, float]:
    optimization = config.get("optimization", {})
    return {
        "alpha": float(optimization.get("alpha_cfe_distance", 1.0)),
        "beta": float(optimization.get("beta_jmas_distance", 1.0)),
        "gamma": float(optimization.get("gamma_bridge_travel", 2.0)),
        "delta_worker_commute": float(optimization.get("delta_worker_commute_profile3", 0.0)),
    }


def _allocation_signature(allocation: dict[int, int]) -> str:
    return ";".join(f"{project_id}:{allocation[project_id]}" for project_id in sorted(allocation))


def run_sensitivity(config_path: Path) -> pd.DataFrame:
    repo_root = config_path.resolve().parent
    config = _read_yaml(config_path)
    scenario = build_scenario(repo_root, config)
    base_weights = _base_weights(config)
    variations = _variations_from_config(config)

    baseline_allocation, baseline_metrics = solve_variant(scenario, PROPOSED_VARIANT, base_weights)
    baseline_signature = _allocation_signature(baseline_allocation)
    rows = []
    allocation_rows = []

    for parameter in ["alpha", "beta", "gamma", "delta_worker_commute"]:
        for variation in variations:
            weights = dict(base_weights)
            weights[parameter] = base_weights[parameter] * (1.0 + variation)
            allocation, metrics = solve_variant(scenario, PROPOSED_VARIANT, weights)
            signature = _allocation_signature(allocation)
            assignment_changes = sum(
                1
                for project_id, plot_id in allocation.items()
                if baseline_allocation.get(project_id) != plot_id
            )
            selected_baseline = set(baseline_allocation.values())
            selected_current = set(allocation.values())
            selected_plot_changes = len(selected_baseline.symmetric_difference(selected_current))
            row = dict(metrics)
            row.update(
                {
                    "parameter": parameter,
                    "variation": variation,
                    "weight_alpha": weights["alpha"],
                    "weight_beta": weights["beta"],
                    "weight_gamma": weights["gamma"],
                    "weight_delta_worker_commute": weights["delta_worker_commute"],
                    "allocation_signature": signature,
                    "same_as_baseline": signature == baseline_signature,
                    "assignment_changes_vs_baseline": assignment_changes,
                    "selected_plot_set_changes_vs_baseline": selected_plot_changes,
                }
            )
            rows.append(row)
            for project_id, plot_id in allocation.items():
                allocation_rows.append(
                    {
                        "parameter": parameter,
                        "variation": variation,
                        "project_id": project_id,
                        "plot_id": plot_id,
                    }
                )

    outputs_dir = repo_root / config.get("paths", {}).get("outputs_dir", "outputs")
    metrics_dir = outputs_dir / "metrics"
    tables_dir = outputs_dir / "tables"
    allocations_dir = outputs_dir / "allocations"
    for directory in [metrics_dir, tables_dir, allocations_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    raw_frame = pd.DataFrame(rows)
    raw_frame.to_csv(metrics_dir / "sensitivity_runs.csv", index=False)
    pd.DataFrame(allocation_rows).to_csv(allocations_dir / "sensitivity_allocations.csv", index=False)

    summary = (
        raw_frame.groupby("parameter")
        .agg(
            runs=("variation", "count"),
            min_objective=("objective_value", "min"),
            max_objective=("objective_value", "max"),
            min_cfe_ext=("cfe_ext", "min"),
            max_cfe_ext=("cfe_ext", "max"),
            min_jmas_ext=("jmas_ext", "min"),
            max_jmas_ext=("jmas_ext", "max"),
            min_profile3_commute=("profile3_avg_commute", "min"),
            max_profile3_commute=("profile3_avg_commute", "max"),
            min_dynamic_border_time=("mean_dynamic_border_time", "min"),
            max_dynamic_border_time=("mean_dynamic_border_time", "max"),
            max_assignment_changes=("assignment_changes_vs_baseline", "max"),
            max_selected_plot_set_changes=("selected_plot_set_changes_vs_baseline", "max"),
            stable_runs=("same_as_baseline", "sum"),
        )
        .reset_index()
    )
    summary["allocation_stability"] = summary["stable_runs"] / summary["runs"]
    summary.to_csv(tables_dir / "sensitivity_summary.csv", index=False)
    write_markdown_table(summary.round(4), tables_dir / "sensitivity_summary.md")

    manifest = {
        "scenario": "synthetic_sensitivity_over_empirical_road_graph",
        "observed_historical_traffic": False,
        "base_weights": base_weights,
        "variations": variations,
        "baseline_variant": PROPOSED_VARIANT,
        "baseline_metrics": baseline_metrics,
    }
    (metrics_dir / "sensitivity_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return raw_frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Run synthetic MILP sensitivity analysis.")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    frame = run_sensitivity(Path(args.config))
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
