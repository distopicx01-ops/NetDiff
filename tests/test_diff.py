import unittest
from CLI.src.scanner.diff import changed_ports, compare_scans, new_devices, removed_devices
OLD = {'192.168.1.1': {'hostname': 'router', 'ports': [80]}, '192.168.1.2': {'hostname': 'pc', 'ports': [22]}}
NEW = {'192.168.1.1': {'hostname': 'router', 'ports': [80, 443]}, '192.168.1.3': {'hostname': 'tv', 'ports': []}}

class TestDiff(unittest.TestCase):

    def test_new_devices(self):
        self.assertEqual(new_devices(OLD, NEW), ['192.168.1.3'])

    def test_removed_devices(self):
        self.assertEqual(removed_devices(OLD, NEW), ['192.168.1.2'])

    def test_changed_ports(self):
        self.assertEqual(changed_ports(OLD, NEW), {'192.168.1.1': {'opened': [443], 'closed': []}})

    def test_compare_scans_same_scan_has_no_changes(self):
        result = compare_scans(OLD, OLD)
        self.assertEqual(result, {'new': [], 'removed': [], 'ports': {}})
if __name__ == '__main__':
    unittest.main()
