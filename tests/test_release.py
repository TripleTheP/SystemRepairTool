"""version.json, CHANGELOG und Versionsnummer im Code müssen zusammenpassen – sonst bietet der Updater eine Version
an, die es nicht gibt, oder das Release bekommt keine Beschreibung."""

import json
import sys
import unittest
from pathlib import Path

from systemrepairtool import REPO, __version__

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_notes  # noqa: E402


class ReleaseTest(unittest.TestCase):
    def test_version_json(self):
        manifest = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))
        self.assertEqual(__version__, manifest["version"])
        self.assertEqual(f"https://github.com/{REPO}/releases/download/v{__version__}/SystemRepairTool_v{__version__}.zip",
                         manifest["download_url"])
        self.assertEqual(f"https://github.com/{REPO}/releases/tag/v{__version__}", manifest["release_url"])

    def test_changelog_has_section(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertTrue(release_notes.section(text, __version__), f"CHANGELOG.md ohne Abschnitt für {__version__}")

    def test_section_ends_at_next_version(self):
        text = "# Änderungen\n\n## 2.0.0 – 2026-10-29\n\n- neu\n\n## 1.1.3\n\n- alt\n"
        self.assertEqual("- neu", release_notes.section(text, "2.0.0"))
        self.assertEqual("", release_notes.section(text, "2.0"))


if __name__ == "__main__":
    unittest.main()
