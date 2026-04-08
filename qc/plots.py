"""Generate QC plots for Nanopore sequencing data."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


COLOR_PALETTE = px.colors.qualitative.Set2


def plot_per_barcode_reads_and_bases(barcode_df: pd.DataFrame) -> go.Figure:
    """Side-by-side bar chart of reads and bases per barcode."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Reads per Barcode", "Bases per Barcode"),
        horizontal_spacing=0.12,
    )

    fig.add_trace(
        go.Bar(
            x=barcode_df["barcode"],
            y=barcode_df["reads"],
            marker_color=COLOR_PALETTE[0],
            name="Reads",
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Bar(
            x=barcode_df["barcode"],
            y=barcode_df["total_bases"],
            marker_color=COLOR_PALETTE[1],
            name="Bases",
        ),
        row=1, col=2,
    )

    fig.update_layout(
        height=450,
        showlegend=False,
        template="plotly_white",
    )
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="Read Count", row=1, col=1)
    fig.update_yaxes(title_text="Total Bases", row=1, col=2)

    return fig


def plot_read_length_distribution(df: pd.DataFrame, n50: int) -> go.Figure:
    """Histogram of read lengths with N50 line."""
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df["length"],
        nbinsx=100,
        marker_color=COLOR_PALETTE[2],
        name="Read Length",
    ))

    fig.add_vline(
        x=n50, line_dash="dash", line_color="red",
        annotation_text=f"N50: {n50:,} bp",
        annotation_position="top right",
    )

    fig.update_layout(
        title="Read Length Distribution",
        xaxis_title="Read Length (bp)",
        yaxis_title="Count",
        template="plotly_white",
        height=400,
    )

    return fig


def plot_read_length_distribution_log(df: pd.DataFrame, n50: int) -> go.Figure:
    """Histogram of log10 read lengths with N50 line."""
    log_lengths = np.log10(df["length"].clip(lower=1))

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=log_lengths,
        nbinsx=100,
        marker_color=COLOR_PALETTE[3],
        name="log10(Read Length)",
    ))

    fig.add_vline(
        x=np.log10(n50), line_dash="dash", line_color="red",
        annotation_text=f"N50: {n50:,} bp",
        annotation_position="top right",
    )

    # Custom tick labels
    tick_vals = list(range(0, int(np.ceil(log_lengths.max())) + 1))
    tick_text = [f"{10**v:,}" for v in tick_vals]

    fig.update_layout(
        title="Read Length Distribution (log scale)",
        xaxis_title="Read Length (bp)",
        yaxis_title="Count",
        xaxis=dict(tickvals=tick_vals, ticktext=tick_text),
        template="plotly_white",
        height=400,
    )

    return fig


def plot_quality_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram of mean read quality scores."""
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df["mean_quality"],
        nbinsx=80,
        marker_color=COLOR_PALETTE[4],
        name="Mean Q-Score",
    ))

    median_q = df["mean_quality"].median()
    fig.add_vline(
        x=median_q, line_dash="dash", line_color="red",
        annotation_text=f"Median: Q{median_q:.1f}",
        annotation_position="top right",
    )

    fig.update_layout(
        title="Read Quality Distribution",
        xaxis_title="Mean Read Quality (Phred)",
        yaxis_title="Count",
        template="plotly_white",
        height=400,
    )

    return fig


def plot_quality_vs_length(df: pd.DataFrame) -> go.Figure:
    """Hexbin-style scatter of quality vs read length."""
    # Subsample for performance if dataset is large
    plot_df = df if len(df) <= 50_000 else df.sample(50_000, random_state=42)

    fig = px.density_heatmap(
        plot_df,
        x="length",
        y="mean_quality",
        nbinsx=100,
        nbinsy=80,
        color_continuous_scale="YlOrRd",
        title="Read Quality vs. Length",
    )

    fig.update_layout(
        xaxis_title="Read Length (bp)",
        yaxis_title="Mean Quality (Phred)",
        template="plotly_white",
        height=450,
    )

    return fig


def plot_per_barcode_quality(barcode_df: pd.DataFrame) -> go.Figure:
    """Bar chart of mean quality per barcode."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=barcode_df["barcode"],
        y=barcode_df["mean_quality"],
        marker_color=COLOR_PALETTE[5],
        name="Mean Quality",
    ))

    fig.update_layout(
        title="Mean Quality per Barcode",
        xaxis_title="Barcode",
        yaxis_title="Mean Quality (Phred)",
        template="plotly_white",
        height=400,
    )
    fig.update_xaxes(tickangle=45)

    return fig


def plot_per_barcode_n50(barcode_df: pd.DataFrame) -> go.Figure:
    """Bar chart of N50 per barcode."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=barcode_df["barcode"],
        y=barcode_df["n50"],
        marker_color=COLOR_PALETTE[6],
        name="N50",
    ))

    fig.update_layout(
        title="N50 per Barcode",
        xaxis_title="Barcode",
        yaxis_title="N50 (bp)",
        template="plotly_white",
        height=400,
    )
    fig.update_xaxes(tickangle=45)

    return fig
