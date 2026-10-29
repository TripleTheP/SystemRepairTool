# Umstellung auf Version 2.0

Stand: 29.10.2026. Dieses Dokument hält fest, was beim Neuaufbau geändert wurde, warum, und was noch von Hand zu
tun ist.

## Ausgangslage

- Im Repository lagen nur `README.md` und `version.json`, kein Quellcode. Die Releases enthielten nur eine mit
  PyInstaller gebaute `.exe` (Python 3.13, tkinter). Der ursprüngliche Quellcode war nicht mehr auffindbar.
- Die Tags `v1.1.1`, `v1.1.2` und `v1.1.3` zeigen alle auf denselben Commit, eine reine Änderung an `version.json`.
- Das Release `v1.1.1` ist kaputt: Die ZIP-Datei ist nur 0,2 MB groß, die `.exe` fehlt.
- Die `README.txt` in der ZIP von 1.1.3 nannte noch Version 1.1.1.
- Der Auto-Updater lud die Datei aus `version.json` ohne Prüfsumme oder Signatur. Wer das Repository oder den
  Download manipuliert, hätte allen Nutzern beliebigen Code unterschieben können, der dann mit
  Administratorrechten läuft.

## Was geändert wurde

### Quellcode neu geschrieben

Das Programm wurde mit denselben Funktionen neu geschrieben und liegt jetzt offen unter `src/systemrepairtool/`.
Es braucht nur die Python-Standardbibliothek.

| Bereich | Änderung | Grund |
|---|---|---|
| Ausführung | Befehle laufen in einem eigenen Thread, die Ausgabe erscheint live | Bei DISM (bis 30 Minuten) wirkte das Fenster sonst eingefroren |
| Ausführung | Abbrechen beendet auch Unterprozesse (`taskkill /T`) | DISM startet `DismHost.exe`, das sonst weiterläuft |
| Ausführung | Systemprogramme mit vollem Pfad aus System32 | Kein gleichnamiges Programm aus dem Arbeitsordner wird gestartet |
| Ausgabe | Erkennung von UTF-16 (SFC) und OEM-Codepage (DISM, ipconfig) | Sonst erscheint SFC mit Leerzeichen zwischen allen Buchstaben, Umlaute werden zerstört |
| Ausgabe | Fortschritt mit `\r` überschreibt die aktuelle Zeile | DISM und SFC würden sonst Hunderte Fortschrittszeilen anhängen |
| Ping | Freie Adresse, Prüfung auf gültige Zeichen | Eine Eingabe wie `-t` würde ping als Option deuten |
| Aufräumen | Nur Dateien älter als eine Stunde, gesperrte überspringen, Verknüpfungen nie folgen | Laufende Installationen bleiben intakt; eine Verknüpfung im Temp-Ordner könnte sonst Dateien außerhalb löschen |
| Aufräumen | Schreibgeschützte Dateien werden entsperrt und gelöscht | Sonst blieben sie dauerhaft liegen |
| Systeminfo | Windows 11 über die Build-Nummer erkannt | Windows 11 meldet in der Registry weiterhin „Windows 10“ |
| Updater | Lädt nichts mehr herunter, öffnet nur die Release-Seite; akzeptiert nur Adressen dieses Repositorys | Siehe Ausgangslage: kein Weg mehr, Schadcode über `version.json` einzuschleusen |
| Rechte | `.exe` fordert Administratorrechte an (UAC-Manifest); ohne sie gibt es einen Hinweis | DISM, SFC und Winsock-Reset brauchen sie |
| Oberfläche | Protokoll speichern, Abbrechen, Beschreibung jeder Aktion in der Statuszeile | Bedienbarkeit |

### Build und Releases automatisiert

- `tools/build.py` baut mit PyInstaller die `.exe` (mit Icon und Versionsangaben in den Dateieigenschaften) und die
  ZIP-Datei mit `.exe`, `tool_icon.ico` und einer aus der Versionsnummer erzeugten `README.txt`. Dazu kommt
  `SHA256SUMS.txt`.
- `.github/workflows/build.yml` testet und baut bei jedem Push und Pull Request.
- `.github/workflows/release.yml` legt automatisch ein Release an, sobald auf `main` eine neue Versionsnummer steht,
  inklusive Prüfsummen und Herkunftsnachweis (Build Provenance). Die Beschreibung kommt aus `CHANGELOG.md`.
- Dependabot hält PyInstaller und die GitHub Actions aktuell.

### Eine Quelle für die Version

Die Versionsnummer steht nur noch in `src/systemrepairtool/__init__.py`. Ein Test prüft, dass `version.json` und
`CHANGELOG.md` dazu passen, damit der Update-Hinweis nie auf ein Release zeigt, das es nicht gibt.

### Kompatibel mit Version 1.1.3

`version.json` behält die Felder `version` und `download_url` und hat zusätzlich `release_url`. Die alte Version
1.1.3 findet darüber das Update auf 2.0.0. Die ZIP-Datei hat denselben Aufbau wie bisher.

### Tests

34 Tests in `tests/` decken Zeichensatz-Erkennung, Fortschrittszeilen, Adressprüfung, Abbrechen, Aufräumen
(alt/neu/gesperrt/schreibgeschützt/Verknüpfungen), Updater, Systeminfos, Versionsabgleich und den Aufbau des
Fensters ab.

## Noch offen (von Hand)

1. **Prüfen und pushen.** Die Änderungen sind bisher nur lokal committet. Beim Push auf `main` entsteht automatisch
   das Release 2.0.0. Bis es fertig ist (einige Minuten), zeigt `version.json` schon auf 2.0.0 – Nutzer von 1.1.3,
   die genau dann starten, bekämen kurz einen Link, der noch nicht funktioniert.
2. **Release v1.1.1 aufräumen.** Die kaputte ZIP-Datei auf GitHub löschen oder das Release als fehlerhaft
   kennzeichnen.
3. **Lizenz wählen.** Ohne `LICENSE`-Datei darf niemand den Code weiterverwenden. Üblich wären MIT oder GPL-3.0.
4. **Signieren (optional).** Unsignierte PyInstaller-Programme, die Systembefehle ausführen, werden von SmartScreen
   und Virenscannern oft blockiert. Wie bei mpp-viewer ginge das kostenlos über die SignPath Foundation.
