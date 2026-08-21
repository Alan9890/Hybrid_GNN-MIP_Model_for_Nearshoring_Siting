"""One-command entry point for the current POC pipeline.

The current implementation delegates to the legacy simulator after documenting
the config path. Future stages should add data audit, STGNN training, ablation,
sensitivity, and report generation here.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from simulate_siting import main as run_siting_simulation


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
    run_siting_simulation()


if __name__ == "__main__":
    main()
