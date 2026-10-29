"""Baut die portable .exe und das Release-ZIP: python tools/build.py

Voraussetzung: pip install -r requirements-build.txt
Ergebnis in dist/release: SystemRepairTool_vX.Y.Z.zip (exe, Icon, README.txt) und SHA256SUMS.txt."""

import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from systemrepairtool import REPO, __version__  # noqa: E402

NAME = f"SystemRepairTool_v{__version__}"
ICON = ROOT / "assets" / "tool_icon.ico"
BUILD = ROOT / "build"
DIST = ROOT / "dist"
RELEASE = DIST / "release"

README = """SystemRepairTool {version}
==========================

Start
-----
1. ZIP-Datei entpacken.
2. "{name}.exe" starten. Windows fragt nach Administratorrechten – die brauchen DISM, SFC und der Winsock-Reset.
3. (Optional) Desktop-Verknüpfung: Rechtsklick auf die .exe -> "Senden an" -> "Desktop (Verknüpfung erstellen)".

Echtheit prüfen
---------------
Die Prüfsummen stehen in SHA256SUMS.txt beim Release. In PowerShell:
  Get-FileHash .\\{name}.zip

Quellcode, Änderungen und neue Versionen:
https://github.com/{repo}
"""

VERSION_INFO = """VSVersionInfo(
  ffi=FixedFileInfo(filevers={numbers}, prodvers={numbers}, mask=0x3f, flags=0x0, OS=0x40004,
                    fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040704b0', [
      StringStruct('CompanyName', 'TripleTheP'),
      StringStruct('FileDescription', 'SystemRepairTool'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', 'SystemRepairTool'),
      StringStruct('OriginalFilename', '{name}.exe'),
      StringStruct('ProductName', 'SystemRepairTool'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1031, 1200])])
  ]
)
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def version_file() -> Path:
    """Versionsangaben für Eigenschaften → Details der .exe."""
    numbers = tuple(int(p) for p in __version__.split("."))
    numbers = (numbers + (0, 0, 0, 0))[:4]
    path = BUILD / "version_info.txt"
    path.write_text(VERSION_INFO.format(numbers=numbers, version=__version__, name=NAME), encoding="utf-8")
    return path


def main():
    BUILD.mkdir(exist_ok=True)
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
        "--uac-admin",  # Windows fragt beim Start nach Administratorrechten
        "--name", NAME,
        "--icon", str(ICON),
        "--add-data", f"{ICON}{os.pathsep}assets",
        "--paths", str(ROOT / "src"),
        "--version-file", str(version_file()),
        "--workpath", str(BUILD / "pyinstaller"),
        "--specpath", str(BUILD),
        "--distpath", str(DIST),
        str(ROOT / "run.py"),
    ], check=True, cwd=ROOT)

    exe = DIST / f"{NAME}.exe"
    RELEASE.mkdir(parents=True, exist_ok=True)
    archive = RELEASE / f"{NAME}.zip"
    readme = README.format(version=__version__, name=NAME, repo=REPO).replace("\n", "\r\n")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(exe, exe.name)
        z.write(ICON, ICON.name)
        z.writestr("README.txt", readme.encode("utf-8-sig"))  # mit BOM, damit der Editor die Umlaute erkennt
    sums = "".join(f"{sha256(p)}  {p.name}\n" for p in (archive, exe))
    (RELEASE / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")
    print(f"Fertig: {archive}")
    print(sums, end="")


if __name__ == "__main__":
    main()
