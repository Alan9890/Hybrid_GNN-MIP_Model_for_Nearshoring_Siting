from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.skipif(importlib.util.find_spec("torch") is None, reason="PyTorch is not installed")


def test_gcn_gru_forward_shape_and_finite_loss() -> None:
    import torch
    from torch import nn

    from src.stgnn.model import GCNGRU, set_deterministic_seed

    set_deterministic_seed(42)
    model = GCNGRU(input_features=2, gcn_hidden=4, gru_hidden=5, output_features=1)
    x = torch.randn(3, 6, 4, 2)
    adjacency = torch.tensor(
        [
            [0, 1, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
        ],
        dtype=torch.float32,
    )
    target = torch.randn(3, 4, 1)
    prediction = model(x, adjacency)
    loss = nn.MSELoss()(prediction, target)
    assert prediction.shape == (3, 4, 1)
    assert torch.isfinite(loss)


def test_checkpoint_reload(tmp_path: Path) -> None:
    import torch

    from src.stgnn.train import STGNNConfig, train_from_arrays

    rng = np.random.default_rng(42)
    x = rng.normal(size=(12, 4, 3, 1)).astype("float32")
    y = rng.normal(size=(12, 3, 1)).astype("float32")
    adjacency = np.ones((3, 3), dtype="float32") - np.eye(3, dtype="float32")
    config = STGNNConfig(epochs=2, batch_size=4, gcn_hidden=4, gru_hidden=4, early_stopping_patience=2)

    metrics = train_from_arrays(x, y, adjacency, config, tmp_path)
    checkpoint = torch.load(metrics["checkpoint"], map_location="cpu")

    assert metrics["status"] == "trained"
    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= 0
    assert "model_state_dict" in checkpoint
