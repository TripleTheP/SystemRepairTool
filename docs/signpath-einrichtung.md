# Code-Signierung über die SignPath Foundation

Dieses Dokument beschreibt die Einrichtung der Code-Signierung für SystemRepairTool über das Open-Source-Programm
der [SignPath Foundation](https://signpath.org).

**Status:** Antrag gestellt am 29.10.2026. Bis zur Bewilligung und Einrichtung werden Releases unsigniert, jedoch mit
Prüfsummen und Herkunftsnachweis veröffentlicht.

## Hintergrund

Unsignierte, mit PyInstaller erstellte Programme, die Systembefehle mit Administratorrechten ausführen, werden von
Windows SmartScreen und Virenscannern häufig als verdächtig eingestuft. Eine Authenticode-Signatur weist den
Herausgeber nach und reduziert solche Warnungen.

Der Release-Workflow (`.github/workflows/release.yml`) ist für die Signierung vorbereitet. Sie wird automatisch
aktiv, sobald die Zugangsdaten im Repository hinterlegt sind.

## Voraussetzungen

| Anforderung | Stand |
|---|---|
| Zwei-Faktor-Authentifizierung für alle beteiligten Konten | erforderlich |
| Öffentliches Repository unter einer OSI-anerkannten Lizenz | erfüllt (GPL-3.0) |
| Veröffentlichte Releases | erfüllt |
| Abschnitt „Code signing policy“ in der README | erfüllt |
| Datenschutzhinweis | erfüllt (README, Abschnitt „Datenschutz“) |

## 1. Antrag

Der Antrag wurde über das Formular unter <https://signpath.org/apply> mit folgenden Angaben gestellt:

| Feld | Angabe |
| --- | --- |
| Project name | SystemRepairTool |
| Repository URL | https://github.com/TripleTheP/SystemRepairTool |
| Homepage URL | https://github.com/TripleTheP/SystemRepairTool |
| Download URL | https://github.com/TripleTheP/SystemRepairTool#herunterladen-und-starten |
| Privacy policy URL | https://github.com/TripleTheP/SystemRepairTool#code-signing-policy |
| Category | Other |
| Maintainer type | Individual maintainer(s) |
| Build system | GitHub Actions |

Die Prüfung durch die SignPath Foundation dauert in der Regel mehrere Tage bis Wochen. Eine Bewilligung ist nicht
garantiert; maßgeblich ist unter anderem die Verbreitung des Projekts.

## 2. Konfiguration in SignPath

Nach der Bewilligung:

1. Im Projekt das vordefinierte Trusted Build System **GitHub.com** verknüpfen.
2. Unter *Artifact Configurations* den Inhalt von
   [`.signpath/artifact-configuration.xml`](../.signpath/artifact-configuration.xml) hinterlegen.
3. Die Signing Policies prüfen: `test-signing` für Testläufe, `release-signing` für Releases.
4. Einen *CI User* mit der Rolle *Submitter* anlegen und dessen API-Token sichern.

## 3. Konfiguration in GitHub

Unter *Settings → Secrets and variables → Actions*:

| Typ | Name | Wert |
| --- | --- | --- |
| Secret | `SIGNPATH_API_TOKEN` | API-Token des CI Users |
| Variable | `SIGNPATH_ORGANIZATION_ID` | Organisations-ID aus SignPath |
| Variable (nur für Testläufe) | `SIGNPATH_SIGNING_POLICY_SLUG` | `test-signing`; nach erfolgreichem Test entfernen |
| Variable (optional) | `SIGNPATH_PROJECT_SLUG` | nur erforderlich, wenn der Projekt-Slug von `SystemRepairTool` abweicht |

## 4. Ablauf eines signierten Releases

1. Version gemäß README (Abschnitt „Veröffentlichung einer neuen Version“) erhöhen und auf `main` übertragen.
2. Der Workflow führt die Tests aus, erstellt die ausführbare Datei und reicht sie bei SignPath ein. Er wartet
   bis zu 60 Minuten auf die Freigabe.
3. Die Signaturanfrage in SignPath freigeben (*Approve*); SignPath benachrichtigt hierzu per E-Mail.
4. Der Workflow prüft die Signatur, erstellt das Release-Archiv und veröffentlicht das Release.
