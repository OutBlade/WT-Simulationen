"""Fetch the newest notebooks from kit-cel/lecture-examples and fix old APIs.

    uv run python tools/update_simulationen.py           # download + fix
    uv run python tools/update_simulationen.py --fix     # only fix the local copy

The Übung notebooks were written for matplotlib < 3.1 and IPython < 4.
The replacements below keep them running on current versions.
"""

import io
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIM = ROOT / "simulationen"
REPO = "kit-cel/lecture-examples"
ZIP_URL = f"https://codeload.github.com/{REPO}/zip/refs/heads/master"
COMMIT_URL = f"https://api.github.com/repos/{REPO}/commits/master"

# notebooks that exist only here (not upstream)
OWN = ["uebung/u5_2D_gaussian.ipynb"]

FIXES = [
    ("normed=True", "density=True"),
    ("from IPython.html.widgets import", "from ipywidgets import"),
    ("; ax.hold(True)", ""),
    ("usetex=matplotlib.checkdep_usetex(False)", "usetex=False"),
    ("np.vstack(random_path(t_samples) for _ in range(50))",
     "np.vstack([random_path(t_samples) for _ in range(50)])"),
]


def fix_notebooks():
    changed = []
    for nb in SIM.rglob("*.ipynb"):
        text = nb.read_text(encoding="utf-8")
        new = text
        for old, rep in FIXES:
            new = new.replace(old, rep)
        if new != text:
            json.loads(new)  # still valid JSON
            nb.write_text(new, encoding="utf-8")
            changed.append(nb.relative_to(SIM).as_posix())
    return changed


def download():
    keep = {p: (SIM / p).read_bytes() for p in OWN if (SIM / p).exists()}
    with urllib.request.urlopen(COMMIT_URL) as r:
        commit = json.load(r)
    with urllib.request.urlopen(ZIP_URL) as r:
        archive = zipfile.ZipFile(io.BytesIO(r.read()))
    prefix = archive.namelist()[0].split("/")[0] + "/"
    shutil.rmtree(SIM / "uebung", ignore_errors=True)
    shutil.rmtree(SIM / "vorlesung", ignore_errors=True)
    for name in archive.namelist():
        if name.endswith("/"):
            continue
        rel = name[len(prefix):]
        if rel == "LICENSE":
            target = SIM / "LICENSE"
        elif rel.startswith(("wt/uebung/", "wt/vorlesung/")):
            target = SIM / rel[len("wt/"):]
        else:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(name))
    for p, data in keep.items():
        (SIM / p).write_bytes(data)
    (SIM / "UPSTREAM.txt").write_text(
        f"{commit['sha']} {commit['commit']['committer']['date'][:10]}\n", encoding="utf-8")
    print("Stand:", commit["sha"][:7], commit["commit"]["committer"]["date"][:10])


if __name__ == "__main__":
    if "--fix" not in sys.argv:
        download()
    for name in fix_notebooks():
        print("angepasst:", name)
