import json
import unittest

from systemrepairtool import updater


def manifest(**values) -> bytes:
    return json.dumps(values).encode()


class UpdaterTest(unittest.TestCase):
    def test_versions(self):
        self.assertTrue(updater.is_newer("2.0.1", "2.0.0"))
        self.assertTrue(updater.is_newer("1.10", "1.9.9"))
        self.assertTrue(updater.is_newer("v2.1", "2.0.9"))
        self.assertFalse(updater.is_newer("2.0", "2.0.0"))
        self.assertFalse(updater.is_newer("1.1.3", "2.0.0"))

    def test_invalid_version(self):
        with self.assertRaises(ValueError):
            updater.parse_version("zwei")

    def test_no_update(self):
        self.assertIsNone(updater.parse_manifest(manifest(version="2.0.0"), "2.0.0"))

    def test_update_with_release_page(self):
        page = updater.RELEASES_URL + "/tag/v2.1.0"
        info = updater.parse_manifest(manifest(version="2.1.0", release_url=page), "2.0.0")
        self.assertEqual(updater.UpdateInfo("2.1.0", page), info)

    def test_foreign_address_is_ignored(self):
        for page in ("https://example.com/boese.exe", updater.RELEASES_URL + ".example.com/x", "file:///C:/x"):
            info = updater.parse_manifest(manifest(version="9.0.0", release_url=page), "2.0.0")
            self.assertEqual(updater.RELEASES_URL, info.page_url, page)

    def test_old_manifest_format(self):
        info = updater.parse_manifest(manifest(version="2.1.0", download_url="https://example.com/x.zip"), "2.0.0")
        self.assertEqual(updater.RELEASES_URL, info.page_url)


if __name__ == "__main__":
    unittest.main()
