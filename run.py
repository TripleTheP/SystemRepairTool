"""Startpunkt für PyInstaller und für den Start aus dem Quellcode: python run.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from systemrepairtool.app import main  # noqa: E402

if __name__ == "__main__":
    main()
