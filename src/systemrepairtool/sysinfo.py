"""Systeminformationen für die Anzeige im Protokoll."""

import ctypes
import os
import platform
import shutil

from . import __version__


def format_bytes(value: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024 or unit == "TB":
            if unit == "B":
                return f"{value:.0f} B"
            return f"{value:.1f} {unit}".replace(".", ",")
        value /= 1024


def format_duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    days, minutes = divmod(minutes, 24 * 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if days:
        parts.append(f"{days} {'Tag' if days == 1 else 'Tage'}")
    parts.append(f"{hours} Std.")
    parts.append(f"{minutes} Min.")
    return ", ".join(parts)


def windows_version() -> str:
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
        def get(name, default=None):
            try:
                return winreg.QueryValueEx(key, name)[0]
            except OSError:
                return default

        name = get("ProductName", "Windows")
        release = get("DisplayVersion") or get("ReleaseId")
        build = str(get("CurrentBuild", ""))
        patch = get("UBR")
    # Windows 11 meldet in ProductName weiterhin „Windows 10“; erkennbar ist es nur an der Build-Nummer
    if build.isdigit() and int(build) >= 22000:
        name = name.replace("Windows 10", "Windows 11")
    text = name
    if release:
        text += f" {release}"
    if build:
        text += f" (Build {build}" + (f".{patch}" if patch is not None else "") + ")"
    return text


def processor() -> str:
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
        name = str(winreg.QueryValueEx(key, "ProcessorNameString")[0]).strip()
    return f"{name}, {os.cpu_count()} logische Kerne"


class _MemoryStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def memory() -> str:
    status = _MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx")
    return (f"{format_bytes(status.ullTotalPhys)} gesamt, {format_bytes(status.ullAvailPhys)} frei "
            f"({status.dwMemoryLoad} % belegt)")


def system_drive() -> str:
    drive = os.environ.get("SystemDrive", "C:") + "\\"
    usage = shutil.disk_usage(drive)
    return f"{drive} {format_bytes(usage.total)} gesamt, {format_bytes(usage.free)} frei"


def uptime() -> str:
    tick = ctypes.windll.kernel32.GetTickCount64
    tick.restype = ctypes.c_ulonglong
    return format_duration(tick() / 1000)


def collect() -> list[tuple[str, str]]:
    """Alle Angaben als (Bezeichnung, Wert); was sich nicht ermitteln lässt, erscheint als „unbekannt“."""
    sources = [
        ("Betriebssystem", windows_version),
        ("Computername", platform.node),
        ("Architektur", platform.machine),
        ("Prozessor", processor),
        ("Arbeitsspeicher", memory),
        ("Systemlaufwerk", system_drive),
        ("Laufzeit seit Start", uptime),
        ("SystemRepairTool", lambda: __version__),
    ]
    result = []
    for label, source in sources:
        try:
            value = str(source()) or "unbekannt"
        except Exception:
            value = "unbekannt"
        result.append((label, value))
    return result
