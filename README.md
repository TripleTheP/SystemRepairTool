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

## Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io), certificate by
[SignPath Foundation](https://signpath.org) – sobald die Aufnahme bewilligt ist; bis dahin sind die Releases nicht
signiert.

- Signiert wird nur `SystemRepairTool_vX.Y.Z.exe`. Sie wird von GitHub Actions aus dem öffentlichen Quellcode dieses
  Repositorys gebaut. Jede Signatur muss einzeln von einem Approver freigegeben werden.
- Die mit PyInstaller eingebundenen Fremdkomponenten (Python-Laufzeit, Tcl/Tk) werden nicht einzeln mit dem
  Projektzertifikat signiert.

| Rolle | Mitglieder |
| --- | --- |
| Committer und Reviewer | [TripleTheP](https://github.com/TripleTheP) |
| Approver | [TripleTheP](https://github.com/TripleTheP) |

**Datenschutz / Privacy:** Beim Start fragt das Programm einmal die Datei
`https://raw.githubusercontent.com/TripleTheP/SystemRepairTool/main/version.json` ab, um auf neue Versionen
hinzuweisen. Dabei werden nur die bei jedem Webseitenaufruf üblichen Daten übertragen (IP-Adresse und die
Programmversion als User-Agent). Darüber hinaus überträgt das Programm keine Informationen an andere Systeme im
Netzwerk, sofern dies nicht ausdrücklich von der Benutzerin oder dem Benutzer veranlasst wird (z. B. Ping, oder die
DISM-Reparatur, die Dateien über Windows Update lädt).
On startup the program fetches the file above once to check for a newer version; only the data inherent to any
web request is transmitted (IP address, program version as user agent). Apart from that, this program will not
transfer any information to other networked systems unless specifically requested by the user.

## Selbst bauen

Voraussetzung: Python 3.13 für Windows (mit tkinter, ist im Installer von python.org enthalten).

```powershell
python run.py                                   # aus dem Quellcode starten
python -m unittest discover -s tests -t . -v          # Tests
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
| `tools/build.py` | Build der .exe mit PyInstaller und Verpacken als ZIP |
| `docs/signpath-einrichtung.md` | Signierung der Releases einrichten |
| `version.json` | Aktuelle Version für den Update-Hinweis |

## Lizenz

Copyright © 2025–2026 TripleTheP. SystemRepairTool ist freie Software unter der
[GNU General Public License, Version 3](LICENSE): Du darfst es nutzen, ändern und weitergeben; geänderte Versionen
müssen ebenfalls unter der GPL-3.0 mit Quellcode weitergegeben werden. Ohne jede Gewährleistung.

---

## English

A portable Windows maintenance tool with a graphical interface: DISM and SFC repair, network diagnostics (IP
configuration, DNS flush, Winsock reset, ping), temp file cleanup and system information. Output is shown live,
running actions can be cancelled and the log can be saved.

Download the latest ZIP from [Releases](https://github.com/TripleTheP/SystemRepairTool/releases), unzip and run the
`.exe` (it asks for administrator rights). Each release ships with `SHA256SUMS.txt` and a GitHub build provenance
attestation. To build from source, see *Selbst bauen* above. Licensed under the [GPL-3.0](LICENSE).
