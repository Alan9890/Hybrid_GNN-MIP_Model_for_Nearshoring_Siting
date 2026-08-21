"""Training and evaluation entry points for the GCN-GRU STGNN."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .traffic_dataset import (
    build_temporal_samples,
    chronological_split_indices,
    discover_traffic_dataset,
    load_discovered_traffic,
)


@dataclass(frozen=True)
class STGNNConfig:
    random_seed: int = 42
    window: int = 12
    gcn_hidden: int = 32
    gru_hidden: int = 64
    gru_layers: int = 1
    learning_rate: float = 0.001
    batch_size: int = 64
    weight_decay: float = 0.00001
    epochs: int = 200
    early_stopping_patience: int = 20


def _load_yaml_config(config_path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    with open(config_path, "r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    return loaded if isinstance(loaded, dict) else {}


def load_stgnn_config(config_path: Path) -> STGNNConfig:
    loaded = _load_yaml_config(config_path)
    stgnn = loaded.get("stgnn", {}) if isinstance(loaded.get("stgnn", {}), dict) else {}
    return STGNNConfig(
        random_seed=int(loaded.get("random_seed", STGNNConfig.random_seed)),
        window=int(stgnn.get("window", STGNNConfig.window)),
        gcn_hidden=int(stgnn.get("gcn_hidden", STGNNConfig.gcn_hidden)),
        gru_hidden=int(stgnn.get("gru_hidden", STGNNConfig.gru_hidden)),
        gru_layers=int(stgnn.get("gru_layers", STGNNConfig.gru_layers)),
        learning_rate=float(stgnn.get("learning_rate", STGNNConfig.learning_rate)),
        batch_size=int(stgnn.get("batch_size", STGNNConfig.batch_size)),
        weight_decay=float(stgnn.get("weight_decay", STGNNConfig.weight_decay)),
        epochs=int(stgnn.get("epochs", STGNNConfig.epochs)),
        early_stopping_patience=int(
            stgnn.get("early_stopping_patience", STGNNConfig.early_stopping_patience)
        ),
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _dense_identity_adjacency(nodes: int):
    import torch

    return torch.eye(nodes, dtype=torch.float32)


def _iter_batches(x, y, batch_size: int):
    for start in range(0, len(x), batch_size):
        stop = start + batch_size
        yield x[start:stop], y[start:stop]


def train_from_arrays(
    x: np.ndarray,
    y: np.ndarray,
    adjacency: np.ndarray,
    config: STGNNConfig,
    outputs_dir: Path,
) -> dict[str, Any]:
    """Train GCN-GRU from prepared NumPy arrays and save metrics/checkpoint."""

    import torch
    from torch import nn

    from .model import GCNGRU, set_deterministic_seed

    set_deterministic_seed(config.random_seed)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir = outputs_dir / "metrics"
    models_dir = outputs_dir / "models"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    train_slice, val_slice, test_slice = chronological_split_indices(len(x))
    train_x = torch.tensor(x[train_slice], dtype=torch.float32)
    train_y = torch.tensor(y[train_slice], dtype=torch.float32)
    val_x = torch.tensor(x[val_slice], dtype=torch.float32)
    val_y = torch.tensor(y[val_slice], dtype=torch.float32)
    test_x = torch.tensor(x[test_slice], dtype=torch.float32)
    test_y = torch.tensor(y[test_slice], dtype=torch.float32)
    adjacency_tensor = torch.tensor(adjacency, dtype=torch.float32)

    model = GCNGRU(
        input_features=x.shape[-1],
        gcn_hidden=config.gcn_hidden,
        gru_hidden=config.gru_hidden,
        output_features=y.shape[-1],
        gru_layers=config.gru_layers,
    )
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    criterion = nn.MSELoss()
    best_val = float("inf")
    best_state = None
    patience_used = 0
    history: list[dict[str, float | int]] = []

    for epoch in range(1, config.epochs + 1):
        model.train()
        losses = []
        for batch_x, batch_y in _iter_batches(train_x, train_y, config.batch_size):
            optimizer.zero_grad()
            predictions = model(batch_x, adjacency_tensor)
            loss = criterion(predictions, batch_y)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))

        model.eval()
        with torch.no_grad():
            val_loss = float(criterion(model(val_x, adjacency_tensor), val_y).detach().cpu())
        train_loss = float(np.mean(losses))
        history.append({"epoch": epoch, "train_mse": train_loss, "val_mse": val_loss})

        if val_loss < best_val:
            best_val = val_loss
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            patience_used = 0
        else:
            patience_used += 1
            if patience_used >= config.early_stopping_patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    checkpoint_path = models_dir / "stgnn_best.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config.__dict__,
            "adjacency_shape": list(adjacency.shape),
        },
        checkpoint_path,
    )

    history_path = metrics_dir / "stgnn_history.csv"
    with open(history_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["epoch", "train_mse", "val_mse"])
        writer.writeheader()
        writer.writerows(history)

    model.eval()
    with torch.no_grad():
        predictions = model(test_x, adjacency_tensor)
        errors = predictions - test_y
        mae = float(torch.mean(torch.abs(errors)).detach().cpu())
        rmse = float(torch.sqrt(torch.mean(errors**2)).detach().cpu())

    metrics = {
        "status": "trained",
        "mae": mae,
        "rmse": rmse,
        "train_samples": len(train_x),
        "validation_samples": len(val_x),
        "test_samples": len(test_x),
        "checkpoint": str(checkpoint_path),
        "history": str(history_path),
    }
    _write_json(metrics_dir / "stgnn_test_metrics.json", metrics)
    return metrics


def train_from_repository_data(config_path: Path, data_dir: Path, outputs_dir: Path) -> dict[str, Any]:
    """Train on empirical traffic data if present; otherwise record a skipped status."""

    config = load_stgnn_config(config_path)
    discovery = discover_traffic_dataset(data_dir)
    status_path = outputs_dir / "metrics" / "stgnn_status.json"
    if discovery is None:
        payload = {
            "status": "skipped_missing_empirical_traffic_data",
            "reason": (
                "No CSV in the data directory contains timestamp, road segment id, "
                "and speed/travel-time target columns required for supervised STGNN training."
            ),
            "data_dir": str(Path(data_dir).resolve()),
            "model_implemented": "src.stgnn.model.GCNGRU",
        }
        _write_json(status_path, payload)
        return payload

    frame = load_discovered_traffic(discovery)
    x, y, node_ids, timestamps = build_temporal_samples(frame, discovery.columns, config.window)
    adjacency = np.eye(len(node_ids), dtype="float32")
    feature_schema = {
        "source": str(discovery.path),
        "source_inside_zip": discovery.source_inside_zip,
        "timestamp_column": discovery.columns.timestamp,
        "segment_column": discovery.columns.segment_id,
        "target_column": discovery.columns.target,
        "node_count": len(node_ids),
        "sample_count": len(x),
        "window": config.window,
        "target_timestamps_start": timestamps[0],
        "target_timestamps_end": timestamps[-1],
        "adjacency_note": "Identity adjacency placeholder; replace with road graph adjacency for empirical deployment.",
    }
    _write_json(outputs_dir / "metrics" / "feature_schema.json", feature_schema)
    return train_from_arrays(x, y, adjacency, config, outputs_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train/evaluate the GCN-GRU STGNN.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--data-dir", default="Datos")
    parser.add_argument("--outputs-dir", default="outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = train_from_repository_data(Path(args.config), Path(args.data_dir), Path(args.outputs_dir))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
