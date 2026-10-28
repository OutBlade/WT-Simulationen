"""Clickable overview of all simulations (ipywidgets)."""

import os
import time
import traceback
from pathlib import Path

import ipywidgets as w
from IPython.display import Markdown, display

from .catalog import GROUPS, SIMS
from .runner import SIM_DIR, CellError, run_notebook

ALL = "Alle"

CSS = """
<style>
.wt-head h2 { margin: 0 0 2px 0; }
.wt-head p { margin: 0; opacity: .75; }
.wt-card { padding: 4px 12px; }
.wt-card h3 { margin: 4px 0 6px 0; }
.wt-note { margin-top: 6px; padding: 4px 8px; border-left: 3px solid #d9822b; }
.wt-status { opacity: .75; }
</style>
"""


def _rel_link(path):
    """Link to the original notebook, relative to the notebook showing the launcher."""
    try:
        return Path(os.path.relpath(path, Path.cwd())).as_posix()
    except ValueError:
        return path.as_posix()


class Launcher:
    def __init__(self):
        self.search = w.Text(placeholder="Suchen, z. B. Grenzwertsatz, Würfel, Test",
                             layout=w.Layout(width="100%"))
        self.group = w.ToggleButtons(options=[ALL] + GROUPS, value=ALL,
                                     style={"button_width": "auto"})
        self.select = w.Select(rows=14, layout=w.Layout(width="42%"))
        self.details = w.Output(layout=w.Layout(width="58%"))
        self.run_btn = w.Button(description="Ausführen", icon="play", button_style="primary",
                                layout=w.Layout(width="160px"))
        self.clear_btn = w.Button(description="Ausgabe leeren", icon="eraser",
                                  layout=w.Layout(width="160px"))
        self.show_text = w.Checkbox(value=True, description="Erklärtexte mitanzeigen", indent=False)
        self.status = w.HTML()
        self.output = w.Output(layout=w.Layout(border="1px solid #8884", padding="8px",
                                               min_height="60px"))

        self.search.observe(lambda _: self._filter(), "value")
        self.group.observe(lambda _: self._filter(), "value")
        self.select.observe(lambda _: self._describe(), "value")
        self.run_btn.on_click(lambda _: self.run_selected())
        self.clear_btn.on_click(lambda _: self._clear())
        self._filter()

    def _filter(self):
        q = self.search.value.strip().lower()
        sims = [s for s in SIMS
                if (self.group.value == ALL or s.group == self.group.value)
                and (not q or q in f"{s.title} {s.about} {s.key}".lower())]
        current = self.select.value
        self.select.options = [(s.title, s) for s in sims]
        if current in sims:
            self.select.value = current
        elif sims:
            self.select.value = sims[0]
        else:
            self.select.value = None
        self._describe()

    def _describe(self):
        sim = self.select.value
        self.run_btn.disabled = sim is None
        self.details.clear_output()
        with self.details:
            if sim is None:
                display(Markdown("Keine Simulation gefunden."))
                return
            note = f"\n\n> {sim.note}" if sim.note else ""
            display(Markdown(
                f"### {sim.title}\n{sim.about}\n\n"
                f"*{sim.group}* · `wt.run(\"{sim.key}\")` · "
                f"[Notebook öffnen]({_rel_link(SIM_DIR / sim.path)}){note}"
            ))

    def _clear(self):
        self.output.clear_output()
        self.status.value = ""

    def run_selected(self):
        sim = self.select.value
        if sim is None:
            return
        self.run_btn.disabled = True
        self.status.value = f"<span class='wt-status'>Läuft: {sim.title} …</span>"
        self.output.clear_output()
        started = time.time()
        ok = True
        with self.output:
            try:
                run_notebook(SIM_DIR / sim.path, show_text=self.show_text.value)
            except CellError:
                ok = False  # traceback is already shown
            except Exception:
                ok = False
                traceback.print_exc()
        took = time.time() - started
        self.status.value = (
            f"<span class='wt-status'>{'Fertig' if ok else 'Abgebrochen mit Fehler'}: "
            f"{sim.title} ({took:.1f} s)</span>"
        )
        self.run_btn.disabled = False

    def show(self):
        head = w.HTML(CSS + "<div class='wt-head'><h2>WT-Simulationen</h2>"
                      "<p>Wahrscheinlichkeitstheorie, KIT. Simulation wählen und auf "
                      "Ausführen klicken.</p></div>")
        controls = w.HBox([self.run_btn, self.clear_btn, self.show_text],
                          layout=w.Layout(align_items="center", gap="12px"))
        self.details.add_class("wt-card")
        ui = w.VBox([
            head,
            self.search,
            self.group,
            w.HBox([self.select, self.details]),
            controls,
            self.status,
            self.output,
        ], layout=w.Layout(gap="8px"))
        display(ui)
