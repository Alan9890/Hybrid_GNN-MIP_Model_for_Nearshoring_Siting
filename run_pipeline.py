"""One-command entry point for the current POC pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from simulate_siting import main as run_siting_simulation
from src.experiments.ablation import run_ablation
from src.experiments.sensitivity import run_sensitivity
from src.stgnn.train import train_from_repository_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the nearshoring siting POC pipeline.")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the pipeline configuration file.",
    )
    parser.add_argument(
        "--force-stgnn-train",
        action="store_true",
        help="Retrain the STGNN stage even if cached metrics already exist.",
    )
    parser.add_argument(
        "--skip-ablation",
        action="store_true",
        help="Skip the ablation study stage.",
    )
    parser.add_argument(
        "--skip-sensitivity",
        action="store_true",
        help="Skip the sensitivity analysis stage.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    print(f"Using config: {config_path.resolve()}")
    metrics_path = Path("outputs") / "metrics" / "stgnn_test_metrics.json"
    if metrics_path.exists() and not args.force_stgnn_train:
        with open(metrics_path, "r", encoding="utf-8") as handle:
            stgnn_result = json.load(handle)
        stgnn_result["status"] = f"cached_{stgnn_result.get('status', 'unknown')}"
    else:
        stgnn_result = train_from_repository_data(config_path, Path("Datos"), Path("outputs"))
    print(f"STGNN stage: {stgnn_result['status']}")
    if not args.skip_ablation:
        ablation = run_ablation(config_path)
        print(f"Ablation stage: wrote {len(ablation)} variant rows")
    if not args.skip_sensitivity:
        sensitivity = run_sensitivity(config_path)
        print(f"Sensitivity stage: wrote {len(sensitivity)} run rows")
    run_siting_simulation()


if __name__ == "__main__":
    main()
