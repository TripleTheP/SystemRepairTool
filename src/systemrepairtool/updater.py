"""Prüft beim Start, ob auf GitHub eine neuere Version liegt.

Lädt selbst nichts herunter und führt nichts aus: Bei einer neuen Version zeigt das Programm nur einen Hinweis, der
die Release-Seite auf GitHub im Browser öffnet. So kann eine manipulierte version.json niemandem Schadcode
unterschieben, der dann mit Administratorrechten liefe."""

import json
import urllib.request
from dataclasses import dataclass

from . import REPO

MANIFEST_URL = f"https://raw.githubusercontent.com/{REPO}/main/version.json"
RELEASES_URL = f"https://github.com/{REPO}/releases"
_MAX_BYTES = 64 * 1024


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    page_url: str


def parse_version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in str(text).strip().removeprefix("v").split("."))


def is_newer(remote: str, current: str) -> bool:
    a, b = parse_version(remote), parse_version(current)
    length = max(len(a), len(b))
    return a + (0,) * (length - len(a)) > b + (0,) * (length - len(b))


def parse_manifest(data: bytes, current: str) -> UpdateInfo | None:
    manifest = json.loads(data)
    version = str(manifest["version"])
    if not is_newer(version, current):
        return None
    page = manifest.get("release_url")
    # Nur Seiten dieses Repositorys öffnen, nie eine beliebige Adresse aus der Datei
    if not isinstance(page, str) or not page.startswith(RELEASES_URL + "/"):
        page = RELEASES_URL
    return UpdateInfo(version, page)


def check(current: str, timeout: float = 5) -> UpdateInfo | None:
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": f"SystemRepairTool/{current}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_manifest(response.read(_MAX_BYTES), current)
