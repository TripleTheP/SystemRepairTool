"""Grafische Oberfläche (tkinter, dunkles Design)."""

import ctypes
import queue
import sys
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import __version__, cleanup, commands, sysinfo, updater

BG = "#1e1f22"
PANEL = "#2b2d31"
BUTTON = "#383a40"
CONSOLE = "#141518"
FG = "#e6e6e6"
MUTED = "#9aa0a6"
ACCENT = "#4f8cff"
OK = "#3fb950"
WARN = "#d29922"
ERROR = "#f85149"
FONT = ("Segoe UI", 10)
MONO = ("Consolas", 10)


def resource_path(relative: str) -> Path:
    """Dateien neben dem Quellcode bzw. im entpackten PyInstaller-Verzeichnis."""
    base = getattr(sys, "_MEIPASS", None) or Path(__file__).resolve().parents[2]
    return Path(base) / relative


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


class App:
    def __init__(self, root: tk.Tk, check_updates: bool = True):
        self.root = root
        self.events: queue.Queue = queue.Queue()
        self.stop = threading.Event()
        self.busy = False
        self.action_buttons: list[ttk.Button] = []
        self.commands = commands.builtin_commands()
        self.splitter = commands.CarriageSplitter()
        self.overwrite_line = False
        self.status_text = "Bereit."

        root.title(f"SystemRepairTool {__version__}")
        root.geometry("1040x660")
        root.minsize(820, 520)
        root.configure(bg=BG)
        try:
            root.iconbitmap(default=str(resource_path("assets/tool_icon.ico")))
        except tk.TclError:
            pass
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._init_style()
        self._build()
        self._write(f"SystemRepairTool {__version__}\n", "head")
        if is_admin():
            self._write("Läuft mit Administratorrechten.\n", "muted")
        else:
            self._write("Ohne Administratorrechte scheitern DISM, SFC und der Winsock-Reset. Das Programm per "
                        "Rechtsklick → „Als Administrator ausführen“ starten.\n", "warn")
        if check_updates:
            threading.Thread(target=self._check_update, daemon=True).start()
        root.after(50, self._poll)

    # Aufbau

    def _init_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, font=FONT, bordercolor=PANEL, focuscolor=ACCENT)
        style.configure("Side.TFrame", background=PANEL)
        style.configure("Section.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("Title.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 13, "bold"))
        style.configure("Status.TLabel", background=BG, foreground=MUTED)
        style.configure("Update.TLabel", background=BG, foreground=ACCENT, font=("Segoe UI", 10, "underline"))
        style.configure("TButton", background=BUTTON, foreground=FG, borderwidth=0, padding=(10, 6), anchor="w")
        style.map("TButton",
                  background=[("disabled", "#2f3136"), ("pressed", ACCENT), ("active", "#45484f")],
                  foreground=[("disabled", "#6b6f76")])
        style.configure("Bar.TButton", anchor="center")
        style.configure("TEntry", fieldbackground=CONSOLE, foreground=FG, insertcolor=FG,
                        bordercolor=BUTTON, lightcolor=BUTTON, darkcolor=BUTTON)
        style.configure("Horizontal.TProgressbar", troughcolor=PANEL, background=ACCENT, bordercolor=PANEL,
                        lightcolor=ACCENT, darkcolor=ACCENT)
        style.configure("Vertical.TScrollbar", background=PANEL, troughcolor=CONSOLE, bordercolor=CONSOLE,
                        arrowcolor=MUTED)

    def _build(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        side = ttk.Frame(self.root, style="Side.TFrame", padding=14)
        side.grid(row=0, column=0, sticky="ns")
        ttk.Label(side, text="SystemRepairTool", style="Title.TLabel").pack(anchor="w", pady=(0, 6))

        self._section(side, "REPARATUR")
        for key in ("dism_scan", "dism_restore", "sfc"):
            self._command_button(side, self.commands[key])

        self._section(side, "NETZWERK")
        for key in ("ipconfig", "flushdns", "winsock"):
            self._command_button(side, self.commands[key])
        ping_row = ttk.Frame(side, style="Side.TFrame")
        ping_row.pack(fill="x", pady=2)
        self.ping_host = tk.StringVar(value="8.8.8.8")
        entry = ttk.Entry(ping_row, textvariable=self.ping_host, width=18)
        entry.pack(side="left", fill="x", expand=True, ipady=3)
        entry.bind("<Return>", lambda _e: self.run_ping())
        self._button(ping_row, "Ping", self.run_ping, "Prüft mit vier Paketen, ob die Adresse erreichbar ist.",
                     side="right", fill="none", padx=(6, 0), pady=0)

        self._section(side, "AUFRÄUMEN")
        self._button(side, "Temporäre Dateien löschen", self.run_cleanup,
                     "Löscht alte Dateien aus Windows\\Temp und AppData\\Local\\Temp. "
                     "Neue und gerade benutzte Dateien bleiben erhalten.")

        self._section(side, "SYSTEM")
        self._button(side, "Systeminformationen", self.run_sysinfo,
                     "Zeigt Windows-Version, Prozessor, Arbeitsspeicher, Systemlaufwerk und Laufzeit.")

        main = ttk.Frame(self.root, padding=(14, 14, 14, 10))
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        self.console = tk.Text(main, bg=CONSOLE, fg=FG, insertbackground=FG, selectbackground="#264f78",
                               relief="flat", borderwidth=0, highlightthickness=0, wrap="word", font=MONO,
                               padx=10, pady=8, state="disabled")
        self.console.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(main, orient="vertical", command=self.console.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.console.configure(yscrollcommand=scroll.set)
        for tag, color in (("head", ACCENT), ("ok", OK), ("warn", WARN), ("error", ERROR), ("muted", MUTED)):
            self.console.tag_configure(tag, foreground=color)
        self.console.tag_configure("head", font=(MONO[0], MONO[1], "bold"))

        bar = ttk.Frame(main)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        bar.columnconfigure(1, weight=1)
        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=140)
        self.progress.grid(row=0, column=0, padx=(0, 10))
        self.status = ttk.Label(bar, text=self.status_text, style="Status.TLabel")
        self.status.grid(row=0, column=1, sticky="w")
        self.update_label = ttk.Label(bar, style="Update.TLabel", cursor="hand2")
        self.update_label.grid(row=0, column=2, padx=10)
        self.cancel_button = ttk.Button(bar, text="Abbrechen", style="Bar.TButton", command=self.cancel)
        self.cancel_button.state(["disabled"])
        self.cancel_button.grid(row=0, column=3, padx=(0, 6))
        ttk.Button(bar, text="Protokoll speichern", style="Bar.TButton", command=self.save_log).grid(
            row=0, column=4, padx=(0, 6))
        ttk.Button(bar, text="Leeren", style="Bar.TButton", command=self.clear_log).grid(row=0, column=5)

    def _section(self, parent, title: str):
        ttk.Label(parent, text=title, style="Section.TLabel").pack(anchor="w", pady=(12, 4))

    def _button(self, parent, text: str, command, description: str, **pack) -> ttk.Button:
        button = ttk.Button(parent, text=text, command=command)
        pack.setdefault("fill", "x")
        pack.setdefault("pady", 2)
        button.pack(**pack)
        # Die Beschreibung erscheint in der Statuszeile, solange die Maus über dem Knopf steht
        button.bind("<Enter>", lambda _e: self.status.configure(text=description))
        button.bind("<Leave>", lambda _e: self.status.configure(text=self.status_text))
        self.action_buttons.append(button)
        return button

    def _command_button(self, parent, command: commands.Command):
        self._button(parent, command.label, lambda: self.run_command(command), command.description)

    # Aktionen

    def run_command(self, command: commands.Command):
        self._start(command.label, lambda emit, stop: commands.run_process(command.args, emit, stop),
                    confirm=command.confirm, hint_after=command.hint_after)

    def run_ping(self):
        host = self.ping_host.get().strip()
        if not commands.valid_host(host):
            messagebox.showerror("Ping", "Bitte einen gültigen Hostnamen oder eine IP-Adresse eingeben.",
                                 parent=self.root)
            return
        self.run_command(commands.ping_command(host))

    def run_cleanup(self):
        dirs = cleanup.temp_dirs()
        hours = cleanup.MIN_AGE_SECONDS // 3600
        listing = "\n".join(f"  • {d}" for d in dirs)
        question = (f"Aufgeräumt werden:\n{listing}\n\nGelöscht werden nur Dateien, die älter als {hours} "
                    f"Stunde{'' if hours == 1 else 'n'} sind. Dateien, die gerade benutzt werden, bleiben "
                    f"erhalten.\n\nFortfahren?")

        def work(emit, stop):
            result = cleanup.clean(dirs, stop=stop)
            emit(f"{result.files} Dateien und {result.dirs} Ordner gelöscht, "
                 f"{sysinfo.format_bytes(result.bytes)} freigegeben.\n")
            if result.skipped:
                emit(f"{result.skipped} Einträge übersprungen (in Benutzung, zu neu oder ohne Berechtigung).\n")
            return 0

        self._start("Temporäre Dateien löschen", work, confirm=question)

    def run_sysinfo(self):
        def work(emit, stop):
            for label, value in sysinfo.collect():
                emit(f"{label + ':':<22}{value}\n")
            return 0

        self._start("Systeminformationen", work)

    def cancel(self):
        if self.busy:
            self.stop.set()
            self._set_status("Wird abgebrochen …")

    def save_log(self):
        path = filedialog.asksaveasfilename(
            parent=self.root, title="Protokoll speichern", defaultextension=".txt",
            initialfile=f"SystemRepairTool_{datetime.now():%Y-%m-%d_%H-%M}.txt",
            filetypes=[("Textdatei", "*.txt"), ("Alle Dateien", "*.*")])
        if not path:
            return
        try:
            Path(path).write_text(self.console.get("1.0", "end-1c"), encoding="utf-8")
        except OSError as ex:
            messagebox.showerror("Protokoll speichern", f"Speichern fehlgeschlagen:\n{ex}", parent=self.root)
            return
        self._set_status(f"Protokoll gespeichert: {path}")

    def clear_log(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def on_close(self):
        if self.busy and not messagebox.askyesno(
                "Beenden", "Es läuft noch eine Aktion. Abbrechen und beenden?", parent=self.root):
            return
        self.stop.set()
        self.root.destroy()

    # Hintergrundarbeit

    def _start(self, title: str, work, confirm: str | None = None, hint_after: str | None = None):
        """Führt work(emit, stop) in einem eigenen Thread aus, damit die Oberfläche bedienbar bleibt."""
        if self.busy:
            return
        if confirm and not messagebox.askyesno(title, confirm, parent=self.root):
            return
        self.busy = True
        self.stop.clear()
        self.splitter = commands.CarriageSplitter()
        self.overwrite_line = False
        for button in self.action_buttons:
            button.state(["disabled"])
        self.cancel_button.state(["!disabled"])
        self.progress.start(12)
        self._set_status(f"{title} läuft …")
        self._write(f"\n▶ {title} – {datetime.now():%d.%m.%Y %H:%M:%S}\n", "head")
        started = time.monotonic()

        def emit(text: str):
            self.events.put(("out", text))

        def run():
            code, error = None, None
            try:
                code = work(emit, self.stop)
            except Exception as ex:
                error = f"{type(ex).__name__}: {ex}"
            self.events.put(("done", title, code, error, hint_after, time.monotonic() - started))

        threading.Thread(target=run, daemon=True).start()

    def _poll(self):
        try:
            for _ in range(500):
                event = self.events.get_nowait()
                if event[0] == "out":
                    self._write_output(event[1])
                elif event[0] == "done":
                    self._finish(*event[1:])
                elif event[0] == "update":
                    self._show_update(event[1])
        except queue.Empty:
            pass
        self.root.after(50, self._poll)

    def _finish(self, title: str, code, error, hint_after, seconds: float):
        self._write_tokens(self.splitter.feed("", final=True))
        if self.console.get("end-2c") != "\n":
            self._write("\n")
        duration = f"{seconds:.0f} s" if seconds < 120 else f"{seconds / 60:.0f} min"
        if error:
            self._write(f"✖ {title} fehlgeschlagen: {error}\n", "error")
        elif self.stop.is_set():
            self._write(f"■ {title} abgebrochen.\n", "warn")
        elif code == 0:
            self._write(f"✔ {title} abgeschlossen ({duration}).\n", "ok")
            if hint_after:
                self._write(hint_after + "\n", "warn")
        else:
            self._write(f"✖ {title} beendet mit Code {code} ({duration}).\n", "error")
        self.busy = False
        self.progress.stop()
        for button in self.action_buttons:
            button.state(["!disabled"])
        self.cancel_button.state(["disabled"])
        self._set_status("Bereit.")

    def _check_update(self):
        try:
            info = updater.check(__version__)
        except Exception:
            info = None  # offline oder GitHub nicht erreichbar: kein Hinweis
        self.events.put(("update", info))

    def _show_update(self, info: updater.UpdateInfo | None):
        if info is None:
            return
        self.update_label.configure(text=f"Version {info.version} verfügbar – zur Download-Seite")
        self.update_label.bind("<Button-1>", lambda _e: webbrowser.open(info.page_url))
        self._write(f"Neue Version {info.version} verfügbar: {info.page_url}\n", "ok")

    # Ausgabe

    def _write_output(self, text: str):
        self._write_tokens(self.splitter.feed(text))

    def _write_tokens(self, tokens):
        self.console.configure(state="normal")
        for token in tokens:
            if token is None:
                self.overwrite_line = True
                continue
            if self.overwrite_line:
                # Fortschrittsanzeige: die aktuelle Zeile ersetzen statt eine neue anzuhängen
                self.console.delete("end-1c linestart", "end-1c")
                self.overwrite_line = False
            self.console.insert("end", token)
        self.console.configure(state="disabled")
        self.console.see("end")

    def _write(self, text: str, tag: str | None = None):
        self.console.configure(state="normal")
        self.console.insert("end", text, tag)
        self.console.configure(state="disabled")
        self.console.see("end")

    def _set_status(self, text: str):
        self.status_text = text
        self.status.configure(text=text)


def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # scharfe Schrift bei Skalierung über 100 %
    except (AttributeError, OSError):
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()
