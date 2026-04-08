"""Parse FASTQ files from Nanopore fastq_pass directory structure."""

import gzip
import os
from pathlib import Path

import numpy as np
import pandas as pd


def _phred_scores(quality_string: str) -> np.ndarray:
    """Convert ASCII quality string to Phred scores (Phred+33)."""
    return np.array([ord(c) - 33 for c in quality_string], dtype=np.float32)


def parse_fastq(filepath: Path) -> tuple[list[dict], bool]:
    """Parse a single FASTQ file (plain or gzipped) and return read-level stats.

    Returns (reads, truncated) where truncated is True if the file ended unexpectedly
    (common during active sequencing runs).
    """
    reads = []
    truncated = False
    opener = gzip.open if filepath.suffix == ".gz" else open

    try:
        with opener(filepath, "rt") as fh:
            while True:
                header = fh.readline().strip()
                if not header:
                    break
                sequence = fh.readline().strip()
                fh.readline()  # + line
                quality = fh.readline().strip()

                if not sequence or not quality or len(quality) != len(sequence):
                    truncated = True
                    break

                scores = _phred_scores(quality)
                reads.append({
                    "read_id": header[1:].split()[0],
                    "length": len(sequence),
                    "mean_quality": float(scores.mean()),
                })
    except (EOFError, gzip.BadGzipFile):
        truncated = True

    return reads, truncated


def parse_fastq_pass(fastq_pass_dir: str, progress_callback=None) -> pd.DataFrame:
    """Parse all FASTQ files in a fastq_pass directory organized by barcode.

    Expected structure:
        fastq_pass/
        ├── barcode01/
        │   ├── file1.fastq.gz
        │   └── file2.fastq.gz
        ├── barcode02/
        │   └── file1.fastq.gz
        └── unclassified/
            └── file1.fastq.gz

    Also handles flat structure (FASTQ files directly in the directory).
    """
    base = Path(fastq_pass_dir)
    if not base.is_dir():
        raise FileNotFoundError(f"Directory not found: {fastq_pass_dir}")

    # Collect all FASTQ files with their barcode assignment
    fastq_files = []

    # Check for barcode subdirectories
    for entry in sorted(base.iterdir()):
        if entry.is_dir():
            for fq in sorted(entry.glob("*.fastq*")):
                fastq_files.append((entry.name, fq))

    # Also check for FASTQ files directly in the base directory (flat structure)
    for fq in sorted(base.glob("*.fastq*")):
        fastq_files.append(("no_barcode", fq))

    if not fastq_files:
        raise FileNotFoundError(
            f"No FASTQ files found in {fastq_pass_dir}. "
            "Expected .fastq or .fastq.gz files in barcode subdirectories or directly in the folder."
        )

    all_reads = []
    truncated_files = []
    total_files = len(fastq_files)

    for i, (barcode, fq_path) in enumerate(fastq_files):
        if progress_callback:
            progress_callback(i / total_files, f"Parsing {fq_path.name} ({barcode})")

        reads, truncated = parse_fastq(fq_path)
        if truncated:
            truncated_files.append(fq_path.name)
        for read in reads:
            read["barcode"] = barcode
        all_reads.extend(reads)

    if progress_callback:
        progress_callback(1.0, "Parsing complete")

    if not all_reads:
        raise ValueError(
            f"No reads could be parsed from {fastq_pass_dir}. "
            "All files may be truncated or empty."
        )

    df = pd.DataFrame(all_reads)
    df["bases"] = df["length"]  # alias for clarity in stats
    return df, truncated_files
