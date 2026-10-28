"""Execute a lecture notebook inside the current kernel and show its output."""

import ast
import importlib.util
import json
import os
import re
import shutil
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from IPython import get_ipython
from IPython.display import Markdown, display

SIM_DIR = Path(__file__).resolve().parent.parent / "simulationen"


class CellError(Exception):
    pass


def notebook_cells(path):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    for cell in nb["cells"]:
        src = cell["source"]
        yield cell["cell_type"], "".join(src) if isinstance(src, list) else src


@contextmanager
def _in_dir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def _fresh_matplotlib():
    import matplotlib
    import matplotlib.pyplot as plt

    plt.close("all")
    matplotlib.rcdefaults()


def _check_browser_imports(code):
    """In JupyterLite packages load only on request; name the missing one clearly."""
    if sys.platform != "emscripten":
        return
    from pyodide.code import find_imports

    names = sorted({m.split(".")[0] for m in find_imports(code)})
    missing = [m for m in names if importlib.util.find_spec(m) is None]
    if missing:
        raise ModuleNotFoundError(
            f"Im Browser noch nicht geladen: {', '.join(missing)}. "
            f"Einmal ausführen: await piplite.install({missing!r})")


def _flush_figures():
    try:
        from matplotlib_inline.backend_inline import flush_figures
    except ImportError:
        import matplotlib.pyplot as plt
        plt.show()
    else:
        flush_figures()


# Most lecture notebooks set usetex=True, which needs a LaTeX installation.
# Without one, matplotlib's own mathtext renders the same labels.
HAS_LATEX = (sys.platform != "emscripten" and shutil.which("latex") is not None
             and not os.environ.get("WTSIM_NO_LATEX"))
_USETEX_ON = re.compile(r"usetex\s*=\s*(True|1)\b")


def _exec_cell(shell, src, ns):
    # Qt windows do not exist in the browser, every plot goes inline
    src = src.replace("%matplotlib qt", "%matplotlib inline")
    if not HAS_LATEX:
        src = _USETEX_ON.sub("usetex=False", src)
    code = shell.transform_cell(src) if shell else src
    _check_browser_imports(code)
    tree = ast.parse(code)
    last = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = ast.Expression(tree.body.pop().value)
    exec(compile(tree, "<simulation>", "exec"), ns)
    if last is not None:
        value = eval(compile(last, "<simulation>", "eval"), ns)
        if value is not None:
            display(value)
    _flush_figures()


def run_notebook(path, show_text=True):
    """Run every code cell of `path` in a fresh namespace.

    Markdown cells are rendered too, so the explanations of the lecture
    appear next to the plots. Returns the namespace, so variables of the
    simulation can be inspected afterwards.
    """
    path = Path(path)
    shell = get_ipython()
    ns = {"__name__": "__main__", "get_ipython": get_ipython}
    _fresh_matplotlib()
    started = time.time()
    with _in_dir(path.parent):
        for kind, src in notebook_cells(path):
            if not src.strip():
                continue
            if kind == "markdown":
                if show_text:
                    display(Markdown(src))
            elif kind == "code":
                try:
                    _exec_cell(shell, src, ns)
                except Exception as exc:
                    if shell:
                        shell.showtraceback()
                    raise CellError(f"{path.name}: {exc}") from exc
    ns["_runtime_s"] = time.time() - started
    return ns
