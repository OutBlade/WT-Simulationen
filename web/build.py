"""Build the in-browser version (JupyterLite) into _site/.

    uv run --no-project --with-requirements web/requirements.txt python web/build.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "web" / "_content"
SKIP = shutil.ignore_patterns("__pycache__", ".ipynb_checkpoints", "*.pdf", "*.png")


def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    shutil.rmtree(ROOT / "_site", ignore_errors=True)
    STAGE.mkdir(parents=True)
    start = json.loads((ROOT / "Start.ipynb").read_text(encoding="utf-8"))
    for cell in start["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"], cell["execution_count"] = [], None
    start["metadata"].pop("widgets", None)
    (STAGE / "Start.ipynb").write_text(json.dumps(start, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copytree(ROOT / "wtsim", STAGE / "wtsim", ignore=SKIP)
    shutil.copytree(ROOT / "simulationen", STAGE / "simulationen", ignore=SKIP)
    subprocess.run(
        [sys.executable, "-m", "jupyterlite_core", "build",
         "--contents", str(STAGE), "--output-dir", str(ROOT / "_site"),
         "--lite-dir", str(ROOT / "web")],
        check=True, cwd=ROOT,
    )
    shutil.rmtree(STAGE)


if __name__ == "__main__":
    main()
