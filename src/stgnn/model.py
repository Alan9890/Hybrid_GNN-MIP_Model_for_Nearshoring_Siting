"""Trainable GCN + GRU implementation for traffic forecasting.

The model follows the manuscript's intended structure:

1. spatial graph convolution with normalized adjacency and self loops;
2. temporal recurrence with a GRU over each node's GCN embedding sequence;
3. a linear prediction head for the next-step node target.
"""

from __future__ import annotations

import random

import numpy as np
import torch
from torch import Tensor, nn


def set_deterministic_seed(seed: int) -> None:
    """Set deterministic seeds for Python, NumPy, and PyTorch."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def normalize_adjacency(adjacency: Tensor) -> Tensor:
    """Return D^-1/2 (A + I) D^-1/2 for a dense adjacency matrix."""

    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
        raise ValueError("adjacency must be a square [nodes, nodes] tensor")
    adjacency = adjacency.float()
    identity = torch.eye(adjacency.shape[0], device=adjacency.device, dtype=adjacency.dtype)
    adjacency_with_loops = adjacency + identity
    degree = adjacency_with_loops.sum(dim=1)
    degree_inv_sqrt = torch.pow(degree.clamp(min=1e-12), -0.5)
    degree_matrix = torch.diag(degree_inv_sqrt)
    return degree_matrix @ adjacency_with_loops @ degree_matrix


class GraphConvolution(nn.Module):
    """Dense GCN layer implementing H' = relu(D^-1/2 A~ D^-1/2 H W)."""

    def __init__(self, in_features: int, out_features: int, activation: nn.Module | None = None) -> None:
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)
        self.activation = activation if activation is not None else nn.ReLU()

    def forward(self, x: Tensor, adjacency: Tensor) -> Tensor:
        """Apply graph convolution.

        Args:
            x: Node features shaped [..., nodes, features].
            adjacency: Dense adjacency matrix shaped [nodes, nodes].
        """

        normalized = normalize_adjacency(adjacency).to(device=x.device, dtype=x.dtype)
        support = self.linear(x)
        convolved = torch.einsum("ij,...jf->...if", normalized, support)
        return self.activation(convolved)


class GCNGRU(nn.Module):
    """GCN-GRU next-step forecaster for node-level traffic targets."""

    def __init__(
        self,
        input_features: int,
        gcn_hidden: int,
        gru_hidden: int,
        output_features: int = 1,
        gru_layers: int = 1,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        self.gcn = GraphConvolution(input_features, gcn_hidden)
        self.gru = nn.GRU(
            input_size=gcn_hidden,
            hidden_size=gru_hidden,
            num_layers=gru_layers,
            batch_first=True,
            dropout=dropout if gru_layers > 1 else 0.0,
        )
        self.head = nn.Linear(gru_hidden, output_features)

    def forward(self, x: Tensor, adjacency: Tensor) -> Tensor:
        """Predict next-step node targets.

        Args:
            x: Batch shaped [batch, window, nodes, input_features].
            adjacency: Dense adjacency matrix shaped [nodes, nodes].

        Returns:
            Tensor shaped [batch, nodes, output_features].
        """

        if x.ndim != 4:
            raise ValueError("x must have shape [batch, window, nodes, features]")
        batch_size, window, nodes, features = x.shape
        gcn_input = x.reshape(batch_size * window, nodes, features)
        gcn_output = self.gcn(gcn_input, adjacency)
        gcn_output = gcn_output.reshape(batch_size, window, nodes, -1)
        node_sequences = gcn_output.permute(0, 2, 1, 3).reshape(batch_size * nodes, window, -1)
        _, hidden = self.gru(node_sequences)
        final_hidden = hidden[-1]
        predictions = self.head(final_hidden)
        return predictions.reshape(batch_size, nodes, -1)
