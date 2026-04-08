# Nanopore Sequencing QC Dashboard

A lightweight browser-based tool for quick quality assessment of Oxford Nanopore sequencing runs. Point it at your `fastq_pass` directory and get an interactive overview of your data.

## What you get

- **Run summary**: total reads, total bases, N50, mean/median quality and read length
- **Per-barcode breakdown**: reads, bases, quality, N50 per barcode (table + plots)
- **Read length distribution**: linear and log-scale histograms with N50 marker
- **Quality overview**: Q-score distribution and quality-vs-length heatmap

## Requirements

- [Conda](https://github.com/conda-forge/miniforge#install) (Miniforge, Miniconda, or Anaconda)

That's it — the launcher script handles everything else.

## Quick start

```bash
git clone <this-repo-url>
cd nanopore-qc
./run.sh
```

On first run, this will:
1. Create a conda environment called `nanopore-qc`
2. Install all dependencies (Python, Streamlit, Plotly, etc.)
3. Launch the dashboard in your browser

Then just paste the path to your `fastq_pass` directory into the text field.

## Desktop shortcut (Windows + WSL2)

To create a clickable desktop icon on Windows:

```bash
./install_shortcut_wsl.sh
```

This places a `Nanopore_QC.bat` on your Windows Desktop. Double-click it to launch the dashboard — it starts WSL, activates conda, and opens the app in your browser automatically.

A Linux `.desktop` shortcut installer is also included (`install_shortcut.sh`) for native Linux desktops.

## Expected data structure

```
fastq_pass/
├── barcode01/
│   ├── reads001.fastq.gz
│   └── reads002.fastq.gz
├── barcode02/
│   └── reads001.fastq.gz
└── unclassified/
    └── reads001.fastq.gz
```

Plain `.fastq` files are also supported. If your files are not organized by barcode subdirectories, the tool will still work — all reads will be assigned to a single group.
