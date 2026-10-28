#!/bin/sh
# macOS / Linux: richtet beim ersten Mal alles ein und oeffnet die WT-Simulationen in JupyterLab.
cd "$(dirname "$0")" || exit 1

if ! command -v uv >/dev/null 2>&1; then
    echo "uv wird installiert, einmalig ..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    PATH="$HOME/.local/bin:$PATH"
fi

exec uv run --frozen jupyter lab Start.ipynb
