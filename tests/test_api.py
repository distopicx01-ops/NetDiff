import os
import tempfile
import unittest
from unittest import mock
_tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
os.environ['DATABASE'] = f'sqlite:///{_tmp.name}/test.db'
from fastapi.testclient import TestClient
from backend.api import app
from backend.monitor import run_check
from database.motor.eng import SessionLocal
FIRST = {'10.0.0.1': {'hostname': 'router', 'ports': [80]}}
SECOND = {'10.0.0.1': {'hostname': 'router', 'ports': [80, 443]}, '10.0.0.9': {'hostname': 'nuevo', 'ports': [135, 445]}}

class TestApi(unittest.TestCase):

    def check(self, devices, snapshot_folder):
        db = SessionLocal()
        try:
            with mock.patch('backend.monitor.scan_network', return_value=devices), mock.patch('backend.monitor.save_snapshot', side_effect=lambda d: None), mock.patch('backend.monitor.load_latest_snapshot', return_value=snapshot_folder):
                return run_check(db, '10.0.0.0/24')
        finally:
            db.close()

    def test_full_flow(self):
        client = TestClient(app)
        self.assertEqual(client.get('/health').json(), {'ok': True})
        self.check(FIRST, None)
        result = self.check(SECOND, FIRST)
        self.assertEqual(result['new'], ['10.0.0.9'])
        status = client.get('/status').json()
        self.assertEqual(status['devices'], 2)
        self.assertEqual(status['operations'], 2)
        devices = {d['ip']: d for d in client.get('/devices').json()}
        self.assertEqual(devices['10.0.0.9']['os_guess'], 'Windows')
        self.assertEqual(devices['10.0.0.1']['open_ports'], [80, 443])
        kinds = [e['kind'] for e in client.get('/events').json()]
        self.assertIn('first_scan', kinds)
        self.assertIn('new_device', kinds)
        self.assertIn('ports_changed', kinds)
        only_new = client.get('/events?kind=new_device').json()
        self.assertEqual(len(only_new), 1)
        detail = client.get('/devices/10.0.0.1').json()
        self.assertEqual(len(detail['history']), 2)
        self.assertEqual(client.get('/devices/1.2.3.4').status_code, 404)
        self.assertEqual(len(client.get('/operations').json()), 2)
if __name__ == '__main__':
    unittest.main()
