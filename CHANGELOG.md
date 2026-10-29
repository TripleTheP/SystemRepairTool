# Änderungen

## 2.0.0 – 2026-10-29

Komplett neu geschrieben, jetzt mit offenem Quellcode im Repository. Die Funktionen sind dieselben, nur
zuverlässiger und sicherer.

**Neu und verbessert**
- Die Ausgabe von DISM, SFC und den Netzwerkbefehlen erscheint live im Fenster; das Fenster friert nicht mehr ein.
- Fortschrittsanzeigen von DISM und SFC werden in einer Zeile aktualisiert, statt das Protokoll zu füllen.
- Die SFC-Ausgabe ist lesbar (SFC schreibt UTF-16; Umlaute aus DISM werden korrekt angezeigt).
- Laufende Aktionen lassen sich abbrechen.
- Protokoll als Textdatei speichern.
- Ping an eine frei wählbare Adresse.
- Systeminformationen: Windows-Version (auch Windows 11 richtig erkannt), Prozessor, Arbeitsspeicher,
  Systemlaufwerk, Laufzeit.
- Beim Start fragt Windows nach Administratorrechten; ohne sie gibt das Programm einen Hinweis.
- Versionsangaben in den Dateieigenschaften der .exe.

**Sicherer**
- Der Update-Hinweis lädt nichts mehr selbst herunter, sondern öffnet nur die Release-Seite auf GitHub.
- Temporäre Dateien: Gelöscht wird nur, was älter als eine Stunde ist; gesperrte Dateien werden übersprungen, und
  Verknüpfungen in andere Ordner werden nie verfolgt.
- Systemprogramme werden mit vollem Pfad aus System32 gestartet.
- Jedes Release enthält SHA256-Prüfsummen und einen Herkunftsnachweis von GitHub.

**Projekt**
- Quellcode unter der GNU General Public License, Version 3.
- Automatische Tests und automatischer Build mit GitHub Actions.
- Releases entstehen automatisch, sobald die Versionsnummer auf main steigt.

## 1.1.3 – 2025-08-21

Letzte Version ohne veröffentlichten Quellcode.
