# Version 2.0: Hintergrund und technische Änderungen

Dieses Dokument beschreibt die Gründe für die Neuentwicklung von SystemRepairTool in Version 2.0, die wesentlichen
technischen Änderungen sowie die Kompatibilität zu früheren Versionen. Eine Übersicht für Anwenderinnen und Anwender
enthält das [Änderungsprotokoll](../CHANGELOG.md).

## Ausgangslage

Bis Version 1.1.3 wurde SystemRepairTool ausschließlich als ausführbare Datei veröffentlicht, die mit PyInstaller
aus Python 3.13 und tkinter erstellt wurde. Der zugehörige Quellcode war nicht Bestandteil des Repositorys und stand
für die Weiterentwicklung nicht mehr zur Verfügung. Darüber hinaus wies die bisherige Lösung folgende Schwächen auf:

- **Update-Mechanismus:** Die Anwendung lud die in `version.json` angegebene Datei ohne Prüfsumme oder Signatur
  herunter. Eine Manipulation des Repositorys oder des Downloads hätte die Ausführung beliebigen Codes mit
  Administratorrechten ermöglicht.
- **Nachvollziehbarkeit:** Releases wurden manuell erstellt. Mehrere Versions-Tags verwiesen auf denselben Commit,
  und ein Release enthielt ein unvollständiges Archiv.
- **Vertrauenswürdigkeit:** Ohne veröffentlichten Quellcode und ohne Signatur war die ausführbare Datei weder
  überprüfbar noch reproduzierbar.

## Vorgehen

Die Anwendung wurde mit identischem Funktionsumfang neu entwickelt. Der Quellcode liegt unter
`src/systemrepairtool/` und verwendet ausschließlich die Python-Standardbibliothek.

## Technische Änderungen

### Anwendung

| Bereich | Änderung | Begründung |
|---|---|---|
| Ausführung | Systembefehle laufen in einem eigenen Thread; die Ausgabe wird fortlaufend angezeigt. | DISM benötigt bis zu 30 Minuten; die Oberfläche bleibt währenddessen bedienbar. |
| Ausführung | Beim Abbrechen wird der gesamte Prozessbaum beendet (`taskkill /T`). | DISM startet Unterprozesse (`DismHost.exe`), die andernfalls weiterlaufen. |
| Ausführung | Systemprogramme werden mit vollständigem Pfad aus System32 aufgerufen. | Verhindert das Starten gleichnamiger Programme aus dem Arbeitsverzeichnis oder dem Suchpfad. |
| Ausgabe | Automatische Erkennung von UTF-16 (SFC) und OEM-Codepage (DISM, ipconfig). | Ohne Erkennung wird die SFC-Ausgabe fehlerhaft dargestellt und Umlaute gehen verloren. |
| Ausgabe | Zeilen mit Wagenrücklauf (`\r`) überschreiben die aktuelle Zeile. | DISM und SFC melden ihren Fortschritt auf diese Weise. |
| Ping | Validierung der Zieladresse. | Eingaben wie `-t` würden andernfalls als Programmoption interpretiert. |
| Bereinigung | Nur Dateien älter als eine Stunde; gesperrte Dateien werden übersprungen; Verknüpfungen werden nicht verfolgt. | Schutz laufender Installationen und von Daten außerhalb der Temp-Verzeichnisse. |
| Bereinigung | Schreibgeschützte Dateien werden vor dem Löschen entsperrt. | Solche Dateien würden andernfalls dauerhaft verbleiben. |
| Systeminformationen | Erkennung von Windows 11 anhand der Build-Nummer. | Windows 11 meldet in der Registrierung weiterhin „Windows 10“. |
| Update-Prüfung | Kein Download mehr; es wird ausschließlich die Release-Seite dieses Repositorys geöffnet. | Beseitigt die beschriebene Möglichkeit zur Einschleusung von Code. |
| Berechtigungen | UAC-Manifest fordert Administratorrechte an; ohne diese erscheint ein Hinweis. | DISM, SFC und das Zurücksetzen von Winsock setzen Administratorrechte voraus. |

### Build und Veröffentlichung

- `tools/build.py` erstellt die ausführbare Datei (mit Symbol und Versionsinformationen) sowie das Release-Archiv
  mit Programm, Symbol, Lizenztext und einer aus der Versionsnummer generierten `README.txt`. Zusätzlich wird
  `SHA256SUMS.txt` erzeugt. Mit `--exe-only` und `--package-only` lassen sich beide Schritte getrennt ausführen,
  sodass die ausführbare Datei zwischen Build und Paketierung signiert werden kann.
- `.github/workflows/build.yml` führt bei jeder Änderung die Tests aus und erstellt die Anwendung.
- `.github/workflows/release.yml` veröffentlicht automatisch ein Release, sobald auf `main` eine neue
  Versionsnummer vorliegt. Das Release enthält Prüfsummen und einen Herkunftsnachweis; die Beschreibung wird aus
  dem Änderungsprotokoll übernommen. Sobald die Zugangsdaten der SignPath Foundation hinterlegt sind, wird die
  ausführbare Datei vor der Veröffentlichung signiert (siehe [signpath-einrichtung.md](signpath-einrichtung.md)).
- Dependabot hält PyInstaller und die verwendeten GitHub Actions aktuell.

### Versionsverwaltung

Die Versionsnummer wird ausschließlich in `src/systemrepairtool/__init__.py` gepflegt. Ein automatisierter Test
stellt sicher, dass `version.json` und das Änderungsprotokoll damit übereinstimmen. Dadurch verweist die
Update-Prüfung stets auf ein existierendes Release.

### Lizenz

Der Quellcode steht unter der GNU General Public License, Version 3. Das Release-Archiv enthält den Lizenztext als
`LICENSE.txt`, wie es die Lizenz für die Weitergabe ausführbarer Programme vorsieht.

## Kompatibilität

`version.json` behält die Felder `version` und `download_url` bei und ergänzt das Feld `release_url`. Installationen
der Version 1.1.3 erkennen Version 2.0.0 daher weiterhin als Update. Das Release-Archiv ist wie bisher aufgebaut.

## Qualitätssicherung

Die automatisierten Tests in `tests/` umfassen:

- Zeichensatzerkennung und Verarbeitung von Fortschrittszeilen
- Validierung von Ping-Zielen sowie Prozessausführung und Abbruch
- Bereinigung (alte, neue, gesperrte und schreibgeschützte Dateien, symbolische Verknüpfungen)
- Update-Prüfung einschließlich der Abwehr fremder Adressen
- Systeminformationen
- Übereinstimmung von Version, `version.json` und Änderungsprotokoll
- Aufbau der Oberfläche und Ablauf eines Vorgangs

## Status

| Punkt | Stand |
|---|---|
| Release 2.0.0 | Veröffentlicht am 29.10.2026 |
| Unvollständiges Release 1.1.1 | Entfernt |
| Code-Signierung | Bei der SignPath Foundation beantragt; Workflow vorbereitet |
