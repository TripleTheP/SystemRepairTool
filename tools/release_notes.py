"""Schreibt den Abschnitt einer Version aus CHANGELOG.md in eine Datei (Beschreibung des GitHub-Releases).

python tools/release_notes.py 2.0.0 build/notes.md"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def section(changelog: str, version: str) -> str:
    lines, inside = [], False
    for line in changelog.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = re.match(rf"## \[?v?{re.escape(version)}\]?(\s|$)", line) is not None
            continue
        if inside:
            lines.append(line)
    return "\n".join(lines).strip()


def main():
    version, target = sys.argv[1], Path(sys.argv[2])
    notes = section((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version) or f"SystemRepairTool {version}"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(notes + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
