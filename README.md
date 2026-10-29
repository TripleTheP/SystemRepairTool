# SystemRepairTool

[![Build](https://github.com/TripleTheP/SystemRepairTool/actions/workflows/build.yml/badge.svg)](https://github.com/TripleTheP/SystemRepairTool/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/TripleTheP/SystemRepairTool)](https://github.com/TripleTheP/SystemRepairTool/releases/latest)
[![Lizenz: GPL-3.0](https://img.shields.io/badge/Lizenz-GPL--3.0-blue)](LICENSE)

SystemRepairTool ist ein portables Wartungswerkzeug für Windows. Es bündelt die gängigen Reparatur- und
Diagnosebefehle des Betriebssystems in einer grafischen Oberfläche und zeigt deren Ausgabe in Echtzeit an. Eine
Installation ist nicht erforderlich. *An English summary is provided [below](#english).*

## Funktionsumfang

| Bereich | Funktionen |
|---|---|
| Reparatur | Prüfung (`DISM /ScanHealth`) und Reparatur (`DISM /RestoreHealth`) des Windows-Abbilds, Prüfung und Wiederherstellung geschützter Systemdateien (`sfc /scannow`) |
| Netzwerk | Anzeige der IP-Konfiguration, Leeren des DNS-Caches, Zurücksetzen des Winsock-Katalogs, Ping an frei wählbare Ziele |
| Bereinigung | Entfernen temporärer Dateien aus `%SystemRoot%\Temp` und `%LOCALAPPDATA%\Temp` |
| Systeminformationen | Windows-Version und Build, Prozessor, Arbeitsspeicher, Systemlaufwerk, Betriebszeit |

Weitere Eigenschaften:

- Ausgabe der Systembefehle in Echtzeit; Fortschrittsanzeigen von DISM und SFC werden in einer Zeile aktualisiert.
- Laufende Vorgänge können abgebrochen werden; das Protokoll lässt sich als Textdatei speichern.
- Hinweis auf neue Versionen beim Programmstart.
- Oberfläche im dunklen Design, angepasst an hohe Bildschirmauflösungen.

## Systemvoraussetzungen

- Windows 10 oder Windows 11, 64 Bit
- Administratorrechte für DISM, SFC und das Zurücksetzen des Winsock-Katalogs

<a name="herunterladen-und-starten"></a>

## Installation

1. Die aktuelle ZIP-Datei von der [Release-Seite](https://github.com/TripleTheP/SystemRepairTool/releases/latest)
   herunterladen.
2. Das Archiv an einen beliebigen Ort entpacken.
3. `SystemRepairTool_vX.Y.Z.exe` starten. Die Anwendung fordert beim Start Administratorrechte an.

### Integrität prüfen

Jedes Release enthält die Datei `SHA256SUMS.txt` mit den Prüfsummen aller Artefakte:

```powershell
Get-FileHash .\SystemRepairTool_vX.Y.Z.zip -Algorithm SHA256
```

Zusätzlich wird für jedes Release ein Herkunftsnachweis (Build Provenance Attestation) erzeugt. Er belegt, dass das
Archiv von GitHub Actions aus dem Quellcode dieses Repositorys gebaut wurde:

```powershell
gh attestation verify SystemRepairTool_vX.Y.Z.zip --repo TripleTheP/SystemRepairTool
```

## Bereinigung temporärer Dateien

Die Bereinigung folgt festen Sicherheitsregeln:

- Es werden ausschließlich Dateien entfernt, die älter als eine Stunde sind.
- Dateien, die von laufenden Programmen verwendet werden, bleiben erhalten.
- Symbolischen Verknüpfungen und Junctions wird nicht gefolgt; Inhalte außerhalb der Temp-Verzeichnisse bleiben
  dadurch unberührt.
- Die Temp-Verzeichnisse selbst werden nicht gelöscht.

## Datenschutz

Beim Programmstart wird einmalig die Datei
`https://raw.githubusercontent.com/TripleTheP/SystemRepairTool/main/version.json` abgerufen, um auf neue Versionen
hinzuweisen. Dabei werden ausschließlich die bei jeder HTTP-Anfrage anfallenden Daten übertragen (IP-Adresse sowie
die Programmversion als User-Agent). Darüber hinaus überträgt die Anwendung keine Daten an andere Systeme im Netzwerk,
sofern dies nicht ausdrücklich durch die Benutzerin oder den Benutzer veranlasst wird – etwa durch einen Ping oder
durch die DISM-Reparatur, die Dateien über Windows Update bezieht.

## Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io), certificate by
[SignPath Foundation](https://signpath.org). Die Aufnahme in das Programm der SignPath Foundation ist beantragt;
bis zur Bewilligung werden die Releases unsigniert veröffentlicht.

- Signiert wird ausschließlich `SystemRepairTool_vX.Y.Z.exe`. Die Datei wird von GitHub Actions aus dem öffentlichen
  Quellcode dieses Repositorys gebaut. Jede Signatur erfordert eine einzelne Freigabe durch einen Approver.
- Die über PyInstaller eingebundenen Fremdkomponenten (Python-Laufzeit, Tcl/Tk) werden nicht gesondert mit dem
  Projektzertifikat signiert.

| Rolle | Mitglieder |
| --- | --- |
| Committer und Reviewer | [TripleTheP](https://github.com/TripleTheP) |
| Approver | [TripleTheP](https://github.com/TripleTheP) |

**Privacy policy:** On startup the program fetches the file named under *Datenschutz* once to check for a newer
version; only the data inherent to any web request is transmitted (IP address, program version as user agent).
Apart from that, this program will not transfer any information to other networked systems unless specifically
requested by the user or the person installing or operating it.

## Entwicklung

### Voraussetzungen

Python 3.13 für Windows einschließlich tkinter (im Installer von python.org enthalten). Die Anwendung selbst
verwendet ausschließlich die Python-Standardbibliothek; PyInstaller wird nur für den Build benötigt.

### Ausführen, testen und bauen

```powershell
python run.py                                      # Start aus dem Quellcode
python -m unittest discover -s tests -t . -v       # Tests
python -m pip install -r requirements-build.txt    # Build-Abhängigkeiten
python tools/build.py                              # .exe und ZIP-Archiv in dist/release
```

### Veröffentlichung einer neuen Version

1. Versionsnummer in [`src/systemrepairtool/__init__.py`](src/systemrepairtool/__init__.py) erhöhen.
2. [`version.json`](version.json) auf dieselbe Version setzen und in [`CHANGELOG.md`](CHANGELOG.md) einen Abschnitt
   für die Version anlegen. Ein automatisierter Test prüft die Übereinstimmung.
3. Änderungen auf `main` übertragen. GitHub Actions führt die Tests aus, baut die Anwendung und veröffentlicht das
   Release einschließlich Prüfsummen und Herkunftsnachweis.

Die Einrichtung der Code-Signierung ist in [`docs/signpath-einrichtung.md`](docs/signpath-einrichtung.md)
beschrieben, die Hintergründe zur Version 2.0 in [`docs/UMSTELLUNG-2.0.md`](docs/UMSTELLUNG-2.0.md).

### Projektstruktur

| Pfad | Inhalt |
|---|---|
| `src/systemrepairtool/app.py` | Grafische Oberfläche |
| `src/systemrepairtool/commands.py` | Systembefehle, Prozessausführung mit Echtzeitausgabe, Zeichensatzerkennung |
| `src/systemrepairtool/cleanup.py` | Bereinigung temporärer Dateien |
| `src/systemrepairtool/sysinfo.py` | Systeminformationen |
| `src/systemrepairtool/updater.py` | Prüfung auf neue Versionen |
| `tests/` | Automatisierte Tests |
| `tools/build.py` | Build der ausführbaren Datei mit PyInstaller und Erstellung des Release-Archivs |
| `tools/release_notes.py` | Release-Beschreibung aus `CHANGELOG.md` |
| `version.json` | Aktuelle Version für die Update-Prüfung |

## Lizenz

Copyright © 2025–2026 TripleTheP

SystemRepairTool ist freie Software und steht unter der
[GNU General Public License, Version 3](LICENSE). Die Software darf genutzt, verändert und weitergegeben werden;
abgeleitete Werke müssen unter derselben Lizenz und mit Quellcode weitergegeben werden. Die Software wird ohne
jegliche Gewährleistung bereitgestellt.

---

## English

SystemRepairTool is a portable maintenance utility for Windows. It combines the operating system's common repair
and diagnostic commands in a graphical interface and displays their output in real time; no installation is
required.

**Features:** checking and repairing the Windows image (DISM), restoring protected system files (SFC), network
diagnostics (IP configuration, DNS cache flush, Winsock reset, ping), safe cleanup of temporary files and system
information. Running operations can be cancelled and the log can be saved.

**Installation:** download the latest ZIP archive from the
[releases page](https://github.com/TripleTheP/SystemRepairTool/releases/latest), extract it and run the `.exe`;
administrator rights are requested on startup. Each release includes SHA-256 checksums and a GitHub build provenance
attestation.

**Requirements:** Windows 10 or 11, 64-bit. **License:** [GPL-3.0](LICENSE).
