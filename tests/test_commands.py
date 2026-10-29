import os
import threading
import time
import unittest

from systemrepairtool import commands


class OutputDecoderTest(unittest.TestCase):
    def test_utf16_output_of_sfc_is_recognized(self):
        data = "Überprüfung 5 % abgeschlossen.\r\n".encode("utf-16-le")
        decoder = commands.OutputDecoder()
        # in zwei Stücke mit ungerader Grenze zerlegt, wie es beim Lesen aus der Pipe passieren kann
        text = decoder.decode(data[:7]) + decoder.decode(data[7:]) + decoder.decode(b"", final=True)
        self.assertEqual("Überprüfung 5 % abgeschlossen.\r\n", text)

    def test_bom_is_removed(self):
        data = "﻿Hallo".encode("utf-16-le")
        self.assertEqual("Hallo", commands.OutputDecoder().decode(data, final=True))

    def test_oem_codepage(self):
        data = "Vorgang erfolgreich abgeschlossen. Größe: 5".encode("cp850")
        self.assertEqual("Vorgang erfolgreich abgeschlossen. Größe: 5",
                         commands.OutputDecoder("cp850").decode(data, final=True))

    def test_ascii_is_not_mistaken_for_utf16(self):
        self.assertNotEqual("utf-16-le", commands.OutputDecoder.detect(b"Windows-IP-Konfiguration\r\n"))


class CarriageSplitterTest(unittest.TestCase):
    def test_progress_lines(self):
        tokens = commands.CarriageSplitter().feed("Start\n[=  10%]\r[== 20%]\rFertig\r\n")
        self.assertEqual(["Start\n[=  10%]", None, "[== 20%]", None, "Fertig\n"], tokens)

    def test_crlf_split_across_chunks(self):
        splitter = commands.CarriageSplitter()
        self.assertEqual(["Zeile"], splitter.feed("Zeile\r"))
        self.assertEqual(["\nweiter"], splitter.feed("\nweiter"))

    def test_trailing_cr_at_end(self):
        splitter = commands.CarriageSplitter()
        splitter.feed("50 %\r")
        self.assertEqual([None], splitter.feed("", final=True))


class HostTest(unittest.TestCase):
    def test_valid(self):
        for host in ("8.8.8.8", "example.com", "::1", "fe80::1%12", "router-1.fritz.box"):
            self.assertTrue(commands.valid_host(host), host)

    def test_invalid(self):
        for host in ("", "-t", "-n 9999 x", "a b", "x;calc", "x&y", "a" * 254):
            self.assertFalse(commands.valid_host(host), host)
        with self.assertRaises(ValueError):
            commands.ping_command("-t")


class CommandsTest(unittest.TestCase):
    def test_full_paths(self):
        for command in commands.builtin_commands().values():
            self.assertTrue(os.path.isabs(command.args[0]), command.key)


@unittest.skipUnless(os.name == "nt", "nur unter Windows")
class RunProcessTest(unittest.TestCase):
    def test_output_and_exit_code(self):
        chunks = []
        code = commands.run_process([os.path.join(commands.system32(), "cmd.exe"), "/c", "echo hallo& exit 3"],
                                    chunks.append, threading.Event())
        self.assertEqual(3, code)
        self.assertIn("hallo", "".join(chunks))

    def test_cancel(self):
        stop = threading.Event()
        threading.Timer(0.5, stop.set).start()
        started = time.monotonic()
        commands.run_process([os.path.join(commands.system32(), "PING.EXE"), "-n", "30", "127.0.0.1"],
                             lambda _t: None, stop)
        self.assertLess(time.monotonic() - started, 10)


if __name__ == "__main__":
    unittest.main()
