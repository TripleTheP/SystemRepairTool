"""Löschen temporärer Dateien – nur was alt genug und nicht gesperrt ist, ohne Verknüpfungen zu folgen."""

import os
import stat
import threading
import time
from dataclasses import dataclass
from pathlib import Path

# Jüngere Dateien gehören oft zu laufenden Installationen oder Programmen und bleiben liegen
MIN_AGE_SECONDS = 60 * 60


@dataclass
class CleanupResult:
    files: int = 0
    dirs: int = 0
    bytes: int = 0
    skipped: int = 0


def temp_dirs() -> list[Path]:
    """Windows\\Temp und der Temp-Ordner des angemeldeten Benutzers, jeweils nur einmal."""
    candidates = [os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Temp")]
    if local := os.environ.get("LOCALAPPDATA"):
        candidates.append(os.path.join(local, "Temp"))
    result, seen = [], set()
    for candidate in candidates:
        key = os.path.normcase(os.path.realpath(candidate))
        if key not in seen and os.path.isdir(candidate):
            seen.add(key)
            result.append(Path(candidate))
    return result


def clean(dirs, min_age: float = MIN_AGE_SECONDS, stop: threading.Event | None = None,
          now: float | None = None) -> CleanupResult:
    """Löscht den Inhalt der Ordner (nie die Ordner selbst). Gesperrte, zu neue Dateien und Verknüpfungen werden
    übersprungen und gezählt."""
    result = CleanupResult()
    cutoff = (time.time() if now is None else now) - min_age
    for directory in dirs:
        _clean(Path(directory), result, cutoff, stop)
    return result


def _clean(directory: Path, result: CleanupResult, cutoff: float, stop: threading.Event | None):
    try:
        with os.scandir(directory) as it:
            entries = list(it)
    except OSError:
        result.skipped += 1
        return
    for entry in entries:
        if stop is not None and stop.is_set():
            return
        try:
            if entry.is_symlink() or entry.is_junction():
                # Einer Verknüpfung zu folgen könnte Dateien außerhalb des Temp-Ordners löschen
                result.skipped += 1
            elif entry.is_dir(follow_symlinks=False):
                # Alter vor dem Leeren bestimmen – danach trägt der Ordner die aktuelle Uhrzeit
                old_enough = entry.stat(follow_symlinks=False).st_mtime < cutoff
                _clean(Path(entry.path), result, cutoff, stop)
                if old_enough:
                    try:
                        os.rmdir(entry.path)
                        result.dirs += 1
                    except OSError:
                        pass  # nicht leer, weil darin etwas übersprungen wurde
            else:
                st = entry.stat(follow_symlinks=False)
                if st.st_mtime >= cutoff:
                    result.skipped += 1
                    continue
                _remove(entry.path, st)
                result.files += 1
                result.bytes += st.st_size
        except OSError:
            result.skipped += 1


def _remove(path: str, st: os.stat_result):
    try:
        os.remove(path)
    except PermissionError:
        if st.st_mode & stat.S_IWRITE:
            raise  # in Benutzung oder keine Berechtigung
        os.chmod(path, stat.S_IWRITE)  # schreibgeschützt
        os.remove(path)
