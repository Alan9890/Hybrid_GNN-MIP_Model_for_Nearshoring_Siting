"""One-command entry point for the current POC pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from simulate_siting import main as run_siting_simulation
from src.stgnn.train import train_from_repository_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the nearshoring siting POC pipeline.")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the pipeline configuration file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    print(f"Using config: {config_path.resolve()}")
    stgnn_result = train_from_repository_data(config_path, Path("Datos"), Path("outputs"))
    print(f"STGNN stage: {stgnn_result['status']}")
    run_siting_simulation()


if __name__ == "__main__":
    main()
