import os
import unittest

from systemrepairtool import sysinfo


class SysinfoTest(unittest.TestCase):
    def test_format_bytes(self):
        self.assertEqual("512 B", sysinfo.format_bytes(512))
        self.assertEqual("1,5 KB", sysinfo.format_bytes(1536))
        self.assertEqual("2,0 GB", sysinfo.format_bytes(2 * 1024 ** 3))

    def test_format_duration(self):
        self.assertEqual("0 Std., 5 Min.", sysinfo.format_duration(5 * 60 + 30))
        self.assertEqual("1 Tag, 2 Std., 3 Min.", sysinfo.format_duration(86400 + 2 * 3600 + 3 * 60))
        self.assertEqual("3 Tage, 0 Std., 0 Min.", sysinfo.format_duration(3 * 86400))

    def test_collect(self):
        items = dict(sysinfo.collect())
        self.assertIn("Betriebssystem", items)
        if os.name == "nt":
            for label in ("Betriebssystem", "Prozessor", "Arbeitsspeicher", "Systemlaufwerk", "Laufzeit seit Start"):
                self.assertNotEqual("unbekannt", items[label], label)


if __name__ == "__main__":
    unittest.main()
