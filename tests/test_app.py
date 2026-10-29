"""Baut das Fenster einmal auf (ohne Update-Prüfung) – fängt Fehler in der Oberfläche ab, die die übrigen Tests nicht
sehen."""

import unittest

try:
    import tkinter as tk
except ImportError:  # z. B. eingebettetes Python ohne Tk
    tk = None


@unittest.skipIf(tk is None, "tkinter fehlt")
class AppTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as ex:
            self.skipTest(f"keine Anzeige: {ex}")
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_run_job_and_progress_output(self):
        from systemrepairtool.app import App

        app = App(self.root, check_updates=False)
        app._start("Test", lambda emit, stop: (emit("10 %\r"), emit("100 %\r\nfertig\n"), 0)[-1])
        while app.busy:
            app._poll()
            self.root.update()
        text = app.console.get("1.0", "end")
        self.assertIn("100 %\nfertig\n", text)
        self.assertNotIn("10 %\n", text.replace("100 %", ""))
        self.assertIn("✔ Test abgeschlossen", text)

    def test_error_in_job_is_shown(self):
        from systemrepairtool.app import App

        app = App(self.root, check_updates=False)
        app._start("Kaputt", lambda emit, stop: 1 / 0)
        while app.busy:
            app._poll()
            self.root.update()
        self.assertIn("✖ Kaputt fehlgeschlagen: ZeroDivisionError", app.console.get("1.0", "end"))


if __name__ == "__main__":
    unittest.main()
