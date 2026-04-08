"""Nanopore Sequencing QC Dashboard — Streamlit app."""

import streamlit as st

from qc.parser import parse_fastq_pass
from qc.stats import run_summary, per_barcode_summary
from qc.plots import (
    plot_per_barcode_reads_and_bases,
    plot_read_length_distribution,
    plot_read_length_distribution_log,
    plot_quality_distribution,
    plot_quality_vs_length,
    plot_per_barcode_quality,
    plot_per_barcode_n50,
)


def format_bases(bases: int) -> str:
    """Human-readable base count."""
    if bases >= 1e9:
        return f"{bases / 1e9:.2f} Gb"
    if bases >= 1e6:
        return f"{bases / 1e6:.2f} Mb"
    if bases >= 1e3:
        return f"{bases / 1e3:.2f} Kb"
    return f"{bases} bp"


def main():
    st.set_page_config(
        page_title="Nanopore QC",
        page_icon=":dna:",
        layout="wide",
    )

    st.title("Nanopore Sequencing QC Dashboard")
    st.markdown(
        "Provide the path to your `fastq_pass` directory to generate a quality overview."
    )

    # --- Input ---
    fastq_path = st.text_input(
        "Path to fastq_pass directory",
        placeholder="/path/to/your/fastq_pass",
    )

    if not fastq_path:
        st.info("Enter the path to your fastq_pass directory above to get started.")
        return

    # --- Parse ---
    try:
        progress_bar = st.progress(0, text="Scanning FASTQ files...")

        def update_progress(fraction, text):
            progress_bar.progress(fraction, text=text)

        df, truncated_files = parse_fastq_pass(fastq_path, progress_callback=update_progress)
        progress_bar.empty()

        if truncated_files:
            st.warning(
                f"{len(truncated_files)} file(s) were truncated (possibly still being written). "
                f"Reads parsed before truncation are included. Files: {', '.join(truncated_files[:10])}"
                + ("..." if len(truncated_files) > 10 else "")
            )
    except FileNotFoundError as e:
        st.error(str(e))
        return
    except Exception as e:
        st.error(f"Error parsing data: {e}")
        return

    # --- Summary Statistics ---
    summary = run_summary(df)
    barcode_df = per_barcode_summary(df)

    st.header("Run Summary")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Reads", f"{summary['total_reads']:,}")
    col2.metric("Total Bases", format_bases(summary['total_bases']))
    col3.metric("N50", f"{summary['n50']:,} bp")
    col4.metric("Mean Quality", f"Q{summary['mean_quality']:.1f}")
    col5.metric("Barcodes", summary['num_barcodes'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mean Read Length", f"{summary['mean_read_length']:,.0f} bp")
    col2.metric("Median Read Length", f"{summary['median_read_length']:,.0f} bp")
    col3.metric("Median Quality", f"Q{summary['median_quality']:.1f}")
    col4.metric("Longest Read", f"{summary['longest_read']:,} bp")

    # --- Per-Barcode Table ---
    st.header("Per-Barcode Summary")
    st.dataframe(
        barcode_df.style.format({
            "reads": "{:,}",
            "total_bases": "{:,}",
            "mean_length": "{:,.0f}",
            "median_length": "{:,.0f}",
            "mean_quality": "{:.1f}",
            "median_quality": "{:.1f}",
            "n50": "{:,}",
            "longest_read": "{:,}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # --- Plots ---
    st.header("Per-Barcode Breakdown")
    st.plotly_chart(
        plot_per_barcode_reads_and_bases(barcode_df), use_container_width=True
    )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(plot_per_barcode_quality(barcode_df), use_container_width=True)
    with right:
        st.plotly_chart(plot_per_barcode_n50(barcode_df), use_container_width=True)

    st.header("Read Length Distribution")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            plot_read_length_distribution(df, summary["n50"]),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            plot_read_length_distribution_log(df, summary["n50"]),
            use_container_width=True,
        )

    st.header("Quality")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(plot_quality_distribution(df), use_container_width=True)
    with right:
        st.plotly_chart(plot_quality_vs_length(df), use_container_width=True)


if __name__ == "__main__":
    main()
