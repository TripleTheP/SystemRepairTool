"""Systembefehle (DISM, SFC, Netzwerk) und ihre Ausführung mit live mitgelesener Ausgabe."""

import codecs
import os
import re
import struct
import subprocess
import threading
from dataclasses import dataclass
from typing import Callable

Emit = Callable[[str], None]

_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


@dataclass(frozen=True)
class Command:
    key: str
    label: str
    description: str
    args: tuple[str, ...]
    confirm: str | None = None
    hint_after: str | None = None


def system32() -> str:
    """Pfad zu System32 – auch aus einem 32-Bit-Prozess heraus, den Windows sonst nach SysWOW64 umleitet (dort
    fehlen z. B. sfc.exe und Teile von DISM)."""
    root = os.environ.get("SystemRoot", r"C:\Windows")
    if struct.calcsize("P") == 4:
        sysnative = os.path.join(root, "Sysnative")
        if os.path.isdir(sysnative):
            return sysnative
    return os.path.join(root, "System32")


def _exe(name: str) -> str:
    # Voller Pfad, damit kein gleichnamiges Programm aus dem Arbeitsverzeichnis oder PATH gestartet wird
    return os.path.join(system32(), name)


def builtin_commands() -> dict[str, Command]:
    commands = [
        Command("dism_scan", "DISM: Windows-Abbild prüfen",
                "Prüft das Windows-Abbild auf Schäden. Ändert nichts, dauert einige Minuten.",
                (_exe("Dism.exe"), "/Online", "/Cleanup-Image", "/ScanHealth")),
        Command("dism_restore", "DISM: Windows-Abbild reparieren",
                "Repariert das Windows-Abbild und lädt dazu bei Bedarf Dateien über Windows Update. "
                "Kann 10–30 Minuten dauern.",
                (_exe("Dism.exe"), "/Online", "/Cleanup-Image", "/RestoreHealth")),
        Command("sfc", "SFC: Systemdateien reparieren",
                "Prüft alle geschützten Systemdateien und ersetzt beschädigte. Am besten nach der DISM-Reparatur.",
                (_exe("sfc.exe"), "/scannow")),
        Command("ipconfig", "IP-Konfiguration anzeigen",
                "Zeigt alle Netzwerkadapter mit Adressen, Gateway und DNS-Servern.",
                (_exe("ipconfig.exe"), "/all")),
        Command("flushdns", "DNS-Cache leeren",
                "Verwirft zwischengespeicherte DNS-Einträge, z. B. wenn eine Seite noch auf eine alte Adresse zeigt.",
                (_exe("ipconfig.exe"), "/flushdns")),
        Command("winsock", "Winsock zurücksetzen",
                "Setzt den Winsock-Katalog zurück. Hilft bei defekten Netzwerkverbindungen; danach ist ein Neustart nötig.",
                (_exe("netsh.exe"), "winsock", "reset"),
                confirm="Der Winsock-Katalog wird auf den Auslieferungszustand zurückgesetzt. Manche VPN- oder "
                        "Sicherheitsprogramme müssen danach neu eingerichtet werden, und Windows muss neu "
                        "gestartet werden.\n\nFortfahren?",
                hint_after="Bitte Windows jetzt neu starten, damit der Winsock-Reset wirksam wird."),
    ]
    return {command.key: command for command in commands}


_HOST = re.compile(r"[A-Za-z0-9.:%\-]+")


def valid_host(host: str) -> bool:
    """Hostname oder IP-Adresse; ein führendes „-“ würde ping als Option deuten."""
    return 0 < len(host) <= 253 and not host.startswith("-") and _HOST.fullmatch(host) is not None


def ping_command(host: str) -> Command:
    if not valid_host(host):
        raise ValueError(f"Ungültige Adresse: {host!r}")
    return Command("ping", f"Ping {host}", "Prüft mit vier Paketen, ob die Adresse erreichbar ist.",
                   (_exe("PING.EXE"), "-n", "4", host))


def console_encoding() -> str:
    """Codepage, in der Konsolenprogramme wie DISM ohne eigene Konsole schreiben (OEM, z. B. cp850)."""
    if os.name == "nt":
        try:
            import ctypes
            encoding = f"cp{ctypes.windll.kernel32.GetOEMCP()}"
            codecs.lookup(encoding)
            return encoding
        except (AttributeError, OSError, LookupError):
            pass
    return "utf-8"


class OutputDecoder:
    """Wandelt Programmausgabe stückweise in Text. SFC schreibt UTF-16, die übrigen Befehle in der OEM-Codepage –
    ohne diese Unterscheidung erscheint die SFC-Ausgabe mit Leerzeichen zwischen allen Buchstaben."""

    def __init__(self, encoding: str | None = None):
        self._encoding = encoding
        self._decoder = None
        self._at_start = True

    def decode(self, data: bytes, final: bool = False) -> str:
        if self._decoder is None:
            if not data and not final:
                return ""
            encoding = self._encoding or self.detect(data)
            self._decoder = codecs.getincrementaldecoder(encoding)(errors="replace")
        text = self._decoder.decode(data, final)
        if self._at_start and text:
            text = text.removeprefix("\ufeff")
            self._at_start = False
        return text

    @staticmethod
    def detect(data: bytes) -> str:
        if data.startswith(codecs.BOM_UTF16_LE) or (len(data) >= 4 and data[1::2].count(0) >= len(data) // 4):
            return "utf-16-le"
        return console_encoding()


class CarriageSplitter:
    """Zerlegt Ausgabe in Textstücke und Wagenrückläufe (None). DISM und SFC schreiben ihren Fortschritt mit „\\r“
    immer wieder in dieselbe Zeile; die Oberfläche überschreibt dann die Zeile, statt Hunderte anzuhängen."""

    def __init__(self):
        self._pending_cr = False

    def feed(self, text: str, final: bool = False) -> list[str | None]:
        if self._pending_cr:
            text = "\r" + text
            self._pending_cr = False
        if text.endswith("\r") and not final:
            # Könnte die erste Hälfte von „\r\n“ sein – erst mit dem nächsten Stück entscheiden
            text = text[:-1]
            self._pending_cr = True
        parts = text.replace("\r\n", "\n").split("\r")
        tokens: list[str | None] = []
        for index, part in enumerate(parts):
            if index:
                tokens.append(None)
            if part:
                tokens.append(part)
        return tokens


def run_process(args, emit: Emit, stop: threading.Event) -> int:
    """Startet ein Programm ohne Konsolenfenster und reicht seine Ausgabe laufend an emit weiter. Wird stop gesetzt,
    endet das Programm samt Unterprozessen (DISM startet z. B. DismHost.exe)."""
    process = subprocess.Popen(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               stdin=subprocess.DEVNULL, creationflags=_NO_WINDOW)

    def watch():
        while process.poll() is None:
            if stop.wait(0.2):
                _kill_tree(process)
                return

    threading.Thread(target=watch, daemon=True).start()
    decoder = OutputDecoder()
    while chunk := process.stdout.read1(4096):
        if text := decoder.decode(chunk):
            emit(text)
    if text := decoder.decode(b"", final=True):
        emit(text)
    process.stdout.close()
    return process.wait()


def _kill_tree(process: subprocess.Popen):
    if os.name == "nt":
        subprocess.run([_exe("taskkill.exe"), "/T", "/F", "/PID", str(process.pid)],
                       capture_output=True, creationflags=_NO_WINDOW)
    if process.poll() is None:
        process.kill()
