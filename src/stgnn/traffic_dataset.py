"""Traffic data discovery and chronological sample construction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

TIMESTAMP_CANDIDATES = ("timestamp", "datetime", "date_time", "fecha_hora", "fecha", "time")
SEGMENT_CANDIDATES = ("road_segment_id", "segment_id", "link_id", "edge_id", "id_segmento", "id")
TARGET_CANDIDATES = ("travel_time", "travel_time_min", "speed", "speed_kph", "velocidad", "tiempo")


@dataclass(frozen=True)
class TrafficColumns:
    timestamp: str
    segment_id: str
    target: str


@dataclass(frozen=True)
class TrafficDiscovery:
    path: Path
    columns: TrafficColumns
    source_inside_zip: str | None = None


def _first_matching_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    lookup = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    return None


def _read_csv_header(path_or_buffer) -> list[str]:
    for encoding in ("utf-8", "latin-1"):
        try:
            return list(pd.read_csv(path_or_buffer, nrows=0, encoding=encoding).columns)
        except UnicodeDecodeError:
            if hasattr(path_or_buffer, "seek"):
                path_or_buffer.seek(0)
            continue
    if hasattr(path_or_buffer, "seek"):
        path_or_buffer.seek(0)
    return list(pd.read_csv(path_or_buffer, nrows=0, encoding_errors="replace").columns)


def infer_traffic_columns(columns: list[str]) -> TrafficColumns | None:
    """Infer required traffic columns from a list of column names."""

    timestamp = _first_matching_column(columns, TIMESTAMP_CANDIDATES)
    segment_id = _first_matching_column(columns, SEGMENT_CANDIDATES)
    target = _first_matching_column(columns, TARGET_CANDIDATES)
    if not (timestamp and segment_id and target):
        return None
    return TrafficColumns(timestamp=timestamp, segment_id=segment_id, target=target)


def discover_traffic_dataset(data_dir: Path) -> TrafficDiscovery | None:
    """Find a CSV with timestamp, segment id, and speed/travel-time target columns."""

    data_dir = Path(data_dir)
    for csv_path in sorted(data_dir.rglob("*.csv")):
        columns = _read_csv_header(csv_path)
        inferred = infer_traffic_columns(columns)
        if inferred:
            return TrafficDiscovery(path=csv_path, columns=inferred)

    for zip_path in sorted(data_dir.rglob("*.zip")):
        with ZipFile(zip_path) as archive:
            for member in sorted(archive.namelist()):
                if not member.lower().endswith(".csv"):
                    continue
                with archive.open(member) as handle:
                    columns = _read_csv_header(handle)
                inferred = infer_traffic_columns(columns)
                if inferred:
                    return TrafficDiscovery(path=zip_path, columns=inferred, source_inside_zip=member)
    return None


def load_discovered_traffic(discovery: TrafficDiscovery) -> pd.DataFrame:
    """Load the discovered CSV, including CSV files stored inside ZIP archives."""

    if discovery.source_inside_zip is None:
        return pd.read_csv(discovery.path)
    with ZipFile(discovery.path) as archive:
        with archive.open(discovery.source_inside_zip) as handle:
            return pd.read_csv(handle)


def build_temporal_samples(
    frame: pd.DataFrame,
    columns: TrafficColumns,
    window: int,
):
    """Build X[t-window:t] -> y[t+1] samples from a traffic dataframe.

    Returns NumPy arrays:
        X: [samples, window, nodes, 1]
        y: [samples, nodes, 1]
        node_ids: segment identifiers matching the node axis
        timestamps: target timestamps matching the sample axis
    """

    import numpy as np

    if window < 1:
        raise ValueError("window must be >= 1")

    working = frame[[columns.timestamp, columns.segment_id, columns.target]].copy()
    working[columns.timestamp] = pd.to_datetime(working[columns.timestamp])
    working = working.dropna()
    pivot = (
        working.pivot_table(
            index=columns.timestamp,
            columns=columns.segment_id,
            values=columns.target,
            aggfunc="mean",
        )
        .sort_index()
        .interpolate(limit_direction="both")
        .dropna(axis=1)
    )
    values = pivot.to_numpy(dtype="float32")
    if len(pivot) <= window:
        raise ValueError(f"Need more than {window} timestamps to build temporal samples")

    x_samples = []
    y_samples = []
    target_timestamps = []
    for idx in range(window, len(pivot)):
        x_samples.append(values[idx - window : idx, :, None])
        y_samples.append(values[idx, :, None])
        target_timestamps.append(pivot.index[idx].isoformat())

    return (
        np.stack(x_samples),
        np.stack(y_samples),
        list(pivot.columns),
        target_timestamps,
    )


def chronological_split_indices(sample_count: int, train_ratio: float = 0.70, val_ratio: float = 0.15):
    """Return chronological train/validation/test slices."""

    if sample_count < 3:
        raise ValueError("At least 3 samples are required for train/validation/test split")
    train_end = max(1, int(sample_count * train_ratio))
    val_end = max(train_end + 1, int(sample_count * (train_ratio + val_ratio)))
    val_end = min(val_end, sample_count - 1)
    return slice(0, train_end), slice(train_end, val_end), slice(val_end, sample_count)
