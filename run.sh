#!/usr/bin/env bash
#
# Nanopore QC Dashboard — one-command launcher
# Creates/activates the conda environment and starts the Streamlit app.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="nanopore-qc"
ENV_FILE="$SCRIPT_DIR/environment.yml"

# --- Locate conda ---
if command -v conda &>/dev/null; then
    CONDA_EXE="$(command -v conda)"
elif [ -f "$HOME/miniforge3/bin/conda" ]; then
    CONDA_EXE="$HOME/miniforge3/bin/conda"
elif [ -f "$HOME/miniconda3/bin/conda" ]; then
    CONDA_EXE="$HOME/miniconda3/bin/conda"
elif [ -f "$HOME/anaconda3/bin/conda" ]; then
    CONDA_EXE="$HOME/anaconda3/bin/conda"
else
    echo "ERROR: conda not found. Please install Miniforge or Miniconda first."
    echo "       https://github.com/conda-forge/miniforge#install"
    exit 1
fi

# Source conda shell functions so 'conda activate' works
eval "$("$CONDA_EXE" shell.bash hook)"

# --- Create or update environment ---
if ! conda env list | grep -q "^${ENV_NAME} "; then
    echo "Creating conda environment '${ENV_NAME}'..."
    conda env create -f "$ENV_FILE"
    echo ""
else
    # Update environment if environment.yml has changed since last update
    ENV_STAMP="$(conda info --envs | grep "^${ENV_NAME} " | awk '{print $NF}')/.env_updated"
    if [ ! -f "$ENV_STAMP" ] || [ "$ENV_FILE" -nt "$ENV_STAMP" ]; then
        echo "Updating conda environment '${ENV_NAME}'..."
        conda env update -f "$ENV_FILE" --prune
        touch "$ENV_STAMP"
        echo ""
    fi
fi

# --- Activate and run ---
conda activate "$ENV_NAME"

echo "Starting Nanopore QC Dashboard..."
echo ""
echo "  Open in your browser:  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop."
echo ""

streamlit run "$SCRIPT_DIR/app.py"
