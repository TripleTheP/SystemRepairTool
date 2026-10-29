# SystemRepairTool

[![Build](https://github.com/TripleTheP/SystemRepairTool/actions/workflows/build.yml/badge.svg)](https://github.com/TripleTheP/SystemRepairTool/actions/workflows/build.yml)

Ein portables Windows-Wartungstool mit grafischer Oberfläche zur Reparatur, Diagnose und Systempflege – ohne
Installation. *English below.*

## Funktionen

| Bereich | Aktion |
|---|---|
| Reparatur | DISM: Windows-Abbild prüfen (`/ScanHealth`) und reparieren (`/RestoreHealth`), SFC (`/scannow`) |
| Netzwerk | IP-Konfiguration, DNS-Cache leeren, Winsock zurücksetzen, Ping an eine beliebige Adresse |
| Aufräumen | Temporäre Dateien in `Windows\Temp` und `AppData\Local\Temp` löschen |
| System | Windows-Version, Prozessor, Arbeitsspeicher, Systemlaufwerk, Laufzeit |

- Die Ausgabe erscheint live, Fortschrittsanzeigen werden in einer Zeile aktualisiert.
- Laufende Aktionen lassen sich abbrechen, das Protokoll lässt sich als Textdatei speichern.
- Beim Start prüft das Programm, ob es eine neue Version gibt, und verlinkt dann die Release-Seite.
- Dunkles Design.

## Herunterladen und starten

1. Unter [Releases](https://github.com/TripleTheP/SystemRepairTool/releases) die aktuelle ZIP-Datei laden.
2. Entpacken und `SystemRepairTool_vX.Y.Z.exe` starten. Windows fragt nach Administratorrechten – die brauchen
   DISM, SFC und der Winsock-Reset.

**Echtheit prüfen:** Zu jedem Release gehört `SHA256SUMS.txt`. Vergleichen mit
`Get-FileHash .\SystemRepairTool_vX.Y.Z.zip` in PowerShell. Außerdem hat jedes Release einen Herkunftsnachweis von
GitHub, der belegt, dass die Datei aus genau diesem Quellcode gebaut wurde:
`gh attestation verify SystemRepairTool_vX.Y.Z.zip --repo TripleTheP/SystemRepairTool`.

## Was beim Aufräumen passiert

Gelöscht wird nur, was älter als eine Stunde ist. Dateien, die gerade ein Programm benutzt, bleiben liegen, ebenso
Verknüpfungen in andere Ordner – denen folgt das Tool nie. Die Ordner `Temp` selbst bleiben erhalten.

## Selbst bauen

Voraussetzung: Python 3.13 für Windows (mit tkinter, ist im Installer von python.org enthalten).

```powershell
python run.py                                   # aus dem Quellcode starten
python -m unittest discover -s tests -v          # Tests
python -m pip install -r requirements-build.txt
python tools/build.py                            # .exe und ZIP in dist/release
```

## Neue Version veröffentlichen

1. Versionsnummer in [`src/systemrepairtool/__init__.py`](src/systemrepairtool/__init__.py) erhöhen.
2. [`version.json`](version.json) auf dieselbe Version setzen und in [`CHANGELOG.md`](CHANGELOG.md) einen Abschnitt
   dafür anlegen (ein Test prüft beides).
3. Auf `main` pushen. GitHub Actions testet, baut und legt das Release samt Prüfsummen an.

## Aufbau

| Datei | Inhalt |
|---|---|
| `src/systemrepairtool/app.py` | Oberfläche |
| `src/systemrepairtool/commands.py` | Systembefehle, Ausführung mit Live-Ausgabe, Zeichensatz-Erkennung |
| `src/systemrepairtool/cleanup.py` | Temporäre Dateien |
| `src/systemrepairtool/sysinfo.py` | Systeminformationen |
| `src/systemrepairtool/updater.py` | Prüfung auf neue Versionen |
| `tools/build.py` | Build der .exe mit PyInstaller |
| `version.json` | Aktuelle Version für den Update-Hinweis |

---

## English

A portable Windows maintenance tool with a graphical interface: DISM and SFC repair, network diagnostics (IP
configuration, DNS flush, Winsock reset, ping), temp file cleanup and system information. Output is shown live,
running actions can be cancelled and the log can be saved.

Download the latest ZIP from [Releases](https://github.com/TripleTheP/SystemRepairTool/releases), unzip and run the
`.exe` (it asks for administrator rights). Each release ships with `SHA256SUMS.txt` and a GitHub build provenance
attestation. To build from source, see *Selbst bauen* above.
