import os
import stat
import tempfile
import threading
import time
import unittest
from pathlib import Path

from systemrepairtool import cleanup

NOW = time.time()
OLD = NOW - 2 * cleanup.MIN_AGE_SECONDS


def make(path: Path, content: bytes = b"x", mtime: float = OLD) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    os.utime(path, (mtime, mtime))
    return path


class CleanupTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "Temp"
        self.root.mkdir()

    def tearDown(self):
        for path in self.root.rglob("*"):
            if path.is_file():
                os.chmod(path, stat.S_IWRITE)
        self._tmp.cleanup()

    def test_old_files_and_dirs_are_deleted(self):
        make(self.root / "alt.tmp", b"12345")
        make(self.root / "ordner" / "unter" / "alt.log", b"123")
        os.utime(self.root / "ordner" / "unter", (OLD, OLD))
        os.utime(self.root / "ordner", (OLD, OLD))

        result = cleanup.clean([self.root], now=NOW)

        self.assertEqual(2, result.files)
        self.assertEqual(2, result.dirs)
        self.assertEqual(8, result.bytes)
        self.assertEqual([], list(self.root.iterdir()))
        self.assertTrue(self.root.is_dir(), "der Temp-Ordner selbst bleibt")

    def test_new_files_stay(self):
        make(self.root / "neu.tmp", mtime=NOW - 60)
        make(self.root / "ordner" / "neu.tmp", mtime=NOW - 60)
        os.utime(self.root / "ordner", (OLD, OLD))

        result = cleanup.clean([self.root], now=NOW)

        self.assertEqual(0, result.files)
        self.assertEqual(2, result.skipped)
        self.assertTrue((self.root / "neu.tmp").exists())
        self.assertTrue((self.root / "ordner" / "neu.tmp").exists())

    def test_read_only_file_is_deleted(self):
        path = make(self.root / "schreibgeschützt.tmp")
        os.chmod(path, stat.S_IREAD)
        os.utime(path, (OLD, OLD))
        self.assertEqual(1, cleanup.clean([self.root], now=NOW).files)
        self.assertFalse(path.exists())

    @unittest.skipUnless(os.name == "nt", "Sperren gibt es nur unter Windows")
    def test_locked_file_is_skipped(self):
        path = make(self.root / "gesperrt.tmp")
        with path.open("rb"):
            # Python öffnet ohne FILE_SHARE_DELETE – Löschen schlägt wie bei einer benutzten Datei fehl
            result = cleanup.clean([self.root], now=NOW)
        self.assertEqual(1, result.skipped)
        self.assertTrue(path.exists())

    def test_links_are_not_followed(self):
        outside = Path(self._tmp.name) / "wichtig"
        make(outside / "behalten.txt")
        try:
            os.symlink(outside, self.root / "link", target_is_directory=True)
        except OSError:
            self.skipTest("Symlinks erfordern hier besondere Rechte")
        cleanup.clean([self.root], now=NOW)
        self.assertTrue((outside / "behalten.txt").exists())

    def test_stop(self):
        for i in range(5):
            make(self.root / f"{i}.tmp")
        stop = threading.Event()
        stop.set()
        self.assertEqual(0, cleanup.clean([self.root], now=NOW, stop=stop).files)

    def test_missing_dir(self):
        self.assertEqual(1, cleanup.clean([self.root / "fehlt"], now=NOW).skipped)

    def test_temp_dirs_have_no_duplicates(self):
        dirs = cleanup.temp_dirs()
        keys = [os.path.normcase(os.path.realpath(d)) for d in dirs]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
