# Änderungsprotokoll

Alle nennenswerten Änderungen an SystemRepairTool werden in dieser Datei dokumentiert. Die Versionsnummern folgen
dem Schema [Semantic Versioning](https://semver.org/lang/de/).

## 2.0.0 – 2026-10-29

Vollständige Neuentwicklung bei unverändertem Funktionsumfang. Der Quellcode ist ab dieser Version öffentlich
verfügbar.

### Hinzugefügt
- Ausgabe von DISM, SFC und den Netzwerkbefehlen in Echtzeit, ohne dass die Oberfläche blockiert.
- Abbrechen laufender Vorgänge einschließlich gestarteter Unterprozesse.
- Speichern des Protokolls als Textdatei.
- Ping an frei wählbare Hostnamen und IP-Adressen.
- Erweiterte Systeminformationen: Windows-Version mit Build-Nummer, Prozessor, Arbeitsspeicher, Systemlaufwerk,
  Betriebszeit.
- Anforderung von Administratorrechten beim Start sowie ein Hinweis bei fehlenden Rechten.
- Versionsangaben in den Dateieigenschaften der ausführbaren Datei.

### Geändert
- Fortschrittsanzeigen von DISM und SFC werden in einer Zeile aktualisiert.
- Korrekte Darstellung der SFC-Ausgabe (UTF-16) und von Umlauten in der DISM-Ausgabe (OEM-Codepage).
- Korrekte Erkennung von Windows 11 anhand der Build-Nummer.

### Sicherheit
- Die Update-Prüfung lädt keine Dateien mehr herunter, sondern verweist ausschließlich auf die Release-Seite dieses
  Repositorys.
- Die Bereinigung entfernt nur Dateien, die älter als eine Stunde sind, überspringt gesperrte Dateien und folgt
  keinen symbolischen Verknüpfungen.
- Systemprogramme werden mit vollständigem Pfad aus dem System32-Verzeichnis gestartet.
- Jedes Release enthält SHA-256-Prüfsummen und einen Herkunftsnachweis (Build Provenance Attestation).

### Projekt
- Veröffentlichung des Quellcodes unter der GNU General Public License, Version 3.
- Automatisierte Tests sowie automatisierter Build und automatisierte Veröffentlichung über GitHub Actions.
- Vorbereitung der Code-Signierung über die SignPath Foundation.

## 1.1.3 – 2025-08-21

Letzte Version vor der Neuentwicklung; der Quellcode dieser Version ist nicht veröffentlicht.
