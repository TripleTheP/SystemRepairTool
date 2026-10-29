# Signierung mit SignPath einrichten

Der Release-Workflow (`.github/workflows/release.yml`) ist fertig vorbereitet. Er signiert die `.exe` automatisch,
sobald die Zugangsdaten von SignPath im Repository hinterlegt sind. Bis dahin entstehen unsignierte Releases mit
Prüfsummen und Herkunftsnachweis.

Warum es sich lohnt: Unsignierte PyInstaller-Programme, die Systembefehle mit Administratorrechten ausführen, werden
von Windows SmartScreen und Virenscannern häufig gewarnt oder blockiert.

## 1. Voraussetzungen

- Zwei-Faktor-Anmeldung (2FA) für das GitHub-Konto ist aktiv. SignPath verlangt sie für alle Beteiligten.
- Das Projekt ist öffentlich, steht unter einer Open-Source-Lizenz (GPL-3.0) und hat bereits Releases. Das ist
  erfüllt.
- Die README enthält den Abschnitt [Code signing policy](../README.md#code-signing-policy). Das ist ebenfalls
  erfüllt.
- Version 2.0.0 ist veröffentlicht, sodass der Quellcode zu den Releases öffentlich nachvollziehbar ist.

## 2. Antrag stellen

Formular: <https://signpath.org/apply>

| Feld | Angabe |
| --- | --- |
| Project name | SystemRepairTool |
| Repository | https://github.com/TripleTheP/SystemRepairTool |
| License | GPL-3.0 |
| Description | Portable Windows maintenance tool with a GUI for DISM/SFC repair, network diagnostics, temp file cleanup and system information |
| Download page | https://github.com/TripleTheP/SystemRepairTool/releases |
| Code signing policy | https://github.com/TripleTheP/SystemRepairTool#code-signing-policy |
| Build system | GitHub Actions (GitHub-hosted runners) |
| Files to sign | `SystemRepairTool.exe` (built with PyInstaller) |

Die Prüfung dauert in der Regel einige Tage bis Wochen. Eine Zusage ist nicht garantiert.

## 3. In SignPath (nach der Zusage)

1. Im Projekt den vordefinierten Trusted Build System **GitHub.com** verknüpfen.
2. Unter *Artifact Configurations* den Inhalt von
   [`.signpath/artifact-configuration.xml`](../.signpath/artifact-configuration.xml) einfügen.
3. Die Signing Policy für Tests heißt meist `test-signing`, die für Releases `release-signing`.
4. Einen *CI User* mit der Rolle *Submitter* anlegen und dessen **API-Token** kopieren.

## 4. In GitHub hinterlegen

Unter *Settings → Secrets and variables → Actions*:

| Art | Name | Wert |
| --- | --- | --- |
| Secret | `SIGNPATH_API_TOKEN` | API-Token des CI Users |
| Variable | `SIGNPATH_ORGANIZATION_ID` | Organisations-ID aus SignPath |
| Variable (nur zum Testen) | `SIGNPATH_SIGNING_POLICY_SLUG` | `test-signing`, danach wieder löschen |
| Variable (falls nötig) | `SIGNPATH_PROJECT_SLUG` | nur, wenn der Projekt-Slug nicht `SystemRepairTool` ist |

## 5. Signiertes Release erzeugen

1. Version in `src/systemrepairtool/__init__.py` und `version.json` erhöhen, Abschnitt in `CHANGELOG.md` anlegen,
   auf `main` pushen.
2. Der Workflow baut und testet, reicht die `.exe` bei SignPath ein und wartet bis zu 60 Minuten auf die Freigabe.
3. In SignPath den Signing Request **freigeben** (Approve). SignPath schickt dazu eine E-Mail.
4. Der Workflow prüft die Signatur, packt das ZIP und veröffentlicht das Release.
