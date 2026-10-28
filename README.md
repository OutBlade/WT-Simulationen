# WT-Simulationen

Alle Simulationen aus Vorlesung und Übung **Wahrscheinlichkeitstheorie** (KIT, CEL) in einem Notebook: Simulation auswählen, **Ausführen** klicken, Plots und Erklärtexte erscheinen direkt darunter. Schieberegler-Simulationen bleiben interaktiv.

## Starten

| Weg | Was man braucht | Dauer |
|---|---|---|
| **Windows:** Doppelklick auf `Start.cmd` | nichts | erstes Mal ca. 2 min, danach Sekunden |
| **macOS / Linux:** `sh start.sh` | nichts | erstes Mal ca. 2 min, danach Sekunden |
| **Browser:** die veröffentlichte Web-Version öffnen | nur einen Browser, auch Tablet/Handy | ca. 20 s bis der Python-Kern geladen ist |
| **VS Code:** `Start.ipynb` öffnen, Kernel `.venv` wählen | Python-Erweiterung | sofort |

`Start.cmd` und `start.sh` installieren beim ersten Mal [uv](https://docs.astral.sh/uv/) (falls nicht vorhanden), legen daraus eine eigene Python-Umgebung mit genau den Versionen aus `uv.lock` an und öffnen JupyterLab mit `Start.ipynb`. Am System wird sonst nichts verändert; alles liegt in diesem Ordner unter `.venv`.

In `Start.ipynb` die erste Zelle mit **Shift + Enter** ausführen.

## Ohne Oberfläche

```python
import wtsim as wt
wt.list()                 # alle Simulationen mit Namen
wt.run("clt")             # Zentraler Grenzwertsatz hier ausführen
ns = wt.run("taxi")       # Teil des Titels reicht; ns enthält die Variablen der Simulation
```

`wt.run` führt das Original-Notebook in einem frischen Namensraum aus. Die Notebooks selbst bleiben unverändert nutzbar: im Launcher auf **Notebook öffnen** klicken.

## Inhalt

| Ordner | Inhalt |
|---|---|
| `Start.ipynb` | Launcher |
| `wtsim/` | Launcher und Runner (`catalog.py` = Liste aller Simulationen mit Titel und Beschreibung) |
| `simulationen/` | die Notebooks aus [kit-cel/lecture-examples](https://github.com/kit-cel/lecture-examples/tree/master/wt), Stand in `UPSTREAM.txt`, Lizenz GPL-2.0 |
| `tools/update_simulationen.py` | holt den neuesten Stand von KIT und passt alte API-Aufrufe an |
| `web/` | Build der Browser-Version (JupyterLite) |

### Anpassungen gegenüber dem Original

- Die Übungs-Notebooks stammen aus matplotlib < 3.1 / IPython < 4. `tools/update_simulationen.py` ersetzt `normed=` durch `density=`, `IPython.html.widgets` durch `ipywidgets` und entfernt `ax.hold`, `checkdep_usetex` sowie einen Generator in `np.vstack`.
- `u5_2D_gaussian.py` braucht PyQt5 und ein eigenes Fenster. `uebung/u5_2D_gaussian.ipynb` ist dieselbe Simulation mit Schiebereglern und Play-Taste, läuft also auch im Browser.
- Die meisten Notebooks setzen `usetex=True` und bräuchten dafür LaTeX. Ist kein LaTeX installiert (und immer im Browser), schaltet der Runner das ab; matplotlib setzt die Formeln dann selbst.
- `size_weight` braucht `Umfragedaten_v1_an.xlsx` aus der Vorlesung, die nicht öffentlich ist. Datei nach `simulationen/vorlesung/ch7_9/` legen.

Rechenzeiten auf einem Laptop: die meisten Simulationen unter 15 s, `kolmogorow_smirnow` und `wlln_cauchy` ca. 1 min, `clt_cauchy` ca. 5 min. Im Browser etwa doppelt so lange. Mit installiertem LaTeX setzt matplotlib die Beschriftungen mit echtem LaTeX; das sieht wie im Skript aus, kann aber deutlich länger dauern (`conditional_dice` 3 min statt 1 s). `WTSIM_NO_LATEX=1` schaltet das ab.

## Aktualisieren

```bash
uv run python tools/update_simulationen.py
```

## Browser-Version bauen

```bash
uv run --no-project --with-requirements web/requirements.txt python web/build.py
```

Ergebnis in `_site/`, ein statischer Ordner für jeden Webserver. Liegt das Repository auf GitHub, baut `.github/workflows/pages.yml` die Seite bei jedem Push auf `main` und veröffentlicht sie über GitHub Pages (Settings → Pages → Source: GitHub Actions).
