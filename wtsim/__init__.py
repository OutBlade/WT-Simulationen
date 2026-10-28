"""WT-Simulationen: run any simulation of the lecture with one click.

    import wtsim as wt
    wt.launcher()        # clickable overview
    wt.run("clt")        # run one simulation directly
    wt.list()            # all names
"""

from .catalog import BY_KEY, GROUPS, SIMS, Sim
from .runner import SIM_DIR, CellError, run_notebook

__all__ = ["launcher", "run", "list", "SIMS", "GROUPS"]


def _find(name):
    if isinstance(name, Sim):
        return name
    key = name.lower().removesuffix(".ipynb")
    if key in BY_KEY:
        return BY_KEY[key]
    hits = [s for s in SIMS if key in s.key or key in s.path.lower() or key in s.title.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise KeyError(f"Keine Simulation '{name}'. wt.list() zeigt alle Namen.")
    raise KeyError(f"'{name}' ist mehrdeutig: " + ", ".join(s.key for s in hits))


def run(name, show_text=True):
    """Run a simulation by key, file name or part of its title."""
    sim = _find(name)
    return run_notebook(SIM_DIR / sim.path, show_text=show_text)


def list():
    """Print all simulations with the name to pass to run()."""
    for group in GROUPS:
        print(group)
        for s in SIMS:
            if s.group == group:
                print(f"  {s.key:26s} {s.title}")


def launcher():
    from .launcher import Launcher
    return Launcher().show()
