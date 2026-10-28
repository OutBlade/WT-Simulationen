@echo off
rem Doppelklick: richtet beim ersten Mal alles ein und oeffnet die WT-Simulationen in JupyterLab.
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo uv wird installiert, einmalig ...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

uv run --frozen jupyter lab Start.ipynb
if errorlevel 1 pause
