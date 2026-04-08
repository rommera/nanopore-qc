"""Compute summary statistics from parsed Nanopore read data."""

import numpy as np
import pandas as pd


def compute_n50(lengths: np.ndarray) -> int:
    """Compute N50: the read length at which 50% of total bases are in reads >= this length."""
    sorted_lengths = np.sort(lengths)[::-1]
    cumsum = np.cumsum(sorted_lengths)
    half_total = cumsum[-1] / 2
    idx = np.searchsorted(cumsum, half_total)
    return int(sorted_lengths[idx])


def run_summary(df: pd.DataFrame) -> dict:
    """Compute overall run summary statistics."""
    return {
        "total_reads": len(df),
        "total_bases": int(df["bases"].sum()),
        "mean_read_length": float(df["length"].mean()),
        "median_read_length": float(df["length"].median()),
        "mean_quality": float(df["mean_quality"].mean()),
        "median_quality": float(df["mean_quality"].median()),
        "n50": compute_n50(df["length"].values),
        "longest_read": int(df["length"].max()),
        "num_barcodes": df["barcode"].nunique(),
    }


def per_barcode_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-barcode statistics."""
    grouped = df.groupby("barcode").agg(
        reads=("length", "count"),
        total_bases=("bases", "sum"),
        mean_length=("length", "mean"),
        median_length=("length", "median"),
        mean_quality=("mean_quality", "mean"),
        median_quality=("mean_quality", "median"),
        n50=("length", lambda x: compute_n50(x.values)),
        longest_read=("length", "max"),
    ).reset_index()

    grouped = grouped.sort_values("reads", ascending=False).reset_index(drop=True)

    # Format integer columns
    for col in ["reads", "total_bases", "n50", "longest_read"]:
        grouped[col] = grouped[col].astype(int)

    return grouped
