import tempfile
import unittest
from CLI.src.scanner.snapshots import load_latest_snapshot, save_snapshot

class TestSnapshots(unittest.TestCase):

    def test_no_snapshot_returns_none(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(load_latest_snapshot(folder))

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as folder:
            data = {'10.0.0.1': {'hostname': 'a', 'ports': [22]}}
            save_snapshot(data, folder)
            self.assertEqual(load_latest_snapshot(folder), data)

    def test_load_returns_the_newest(self):
        with tempfile.TemporaryDirectory() as folder:
            save_snapshot({'1.1.1.1': {'hostname': '', 'ports': []}}, folder)
            newer = {'2.2.2.2': {'hostname': '', 'ports': []}}
            save_snapshot(newer, folder)
            self.assertEqual(load_latest_snapshot(folder), newer)
if __name__ == '__main__':
    unittest.main()
