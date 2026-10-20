import os
import tempfile
import unittest
from unittest import mock
import httpx

_tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
os.environ['DATABASE'] = f'sqlite+aiosqlite:///{_tmp.name}/test.db'
os.environ['JWT_SECRET'] = 'test-secret-key-at-least-32-bytes-long-for-hmac-sha256'

from backend.api import app
from backend.monitor import run_check
from database.motor.eng import AsyncSessionLocal, init_db

FIRST = {'10.0.0.1': {'hostname': 'router', 'ports': [80]}}
SECOND = {'10.0.0.1': {'hostname': 'router', 'ports': [80, 443]}, '10.0.0.9': {'hostname': 'nuevo', 'ports': [135, 445]}}

class TestApi(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_db()

    async def check(self, devices, snapshot_folder):
        async with AsyncSessionLocal() as db:
            with mock.patch('backend.monitor.scan_network', return_value=devices), \
                 mock.patch('backend.monitor.save_snapshot', side_effect=lambda d: None), \
                 mock.patch('backend.monitor.load_latest_snapshot', return_value=snapshot_folder):
                return await run_check(db, '10.0.0.0/24')

    async def test_full_flow(self):
        with mock.patch('backend.monitor.scan_network', return_value=SECOND), \
             mock.patch('backend.monitor.save_snapshot', side_effect=lambda d: None), \
             mock.patch('backend.monitor.load_latest_snapshot', return_value=FIRST):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
                res_health = await client.get('/health')
                self.assertEqual(res_health.json(), {'ok': True})

                res_reg = await client.post('/auth/register', json={'username': 'admin', 'password': 'secretpassword'})
                self.assertEqual(res_reg.status_code, 200)
                token = res_reg.json()['access_token']
                self.assertTrue(len(token) > 10)

                res_login = await client.post('/auth/login', json={'username': 'admin', 'password': 'secretpassword'})
                self.assertEqual(res_login.status_code, 200)

                await self.check(FIRST, None)
                result = await self.check(SECOND, FIRST)
                self.assertEqual(result['new'], ['10.0.0.9'])

                res_status = await client.get('/status')
                status_data = res_status.json()
                self.assertEqual(status_data['devices'], 2)
                self.assertEqual(status_data['operations'], 2)

                res_devices = await client.get('/devices')
                devs = {d['ip']: d for d in res_devices.json()}
                self.assertEqual(devs['10.0.0.9']['os_guess'], 'Windows')
                self.assertEqual(devs['10.0.0.1']['open_ports'], [80, 443])

                res_events = await client.get('/events')
                kinds = [e['kind'] for e in res_events.json()]
                self.assertIn('first_scan', kinds)
                self.assertIn('new_device', kinds)
                self.assertIn('ports_changed', kinds)

                res_dev = await client.get('/devices/10.0.0.1')
                self.assertEqual(res_dev.json()['ip'], '10.0.0.1')
                res_404 = await client.get('/devices/1.2.3.4')
                self.assertEqual(res_404.status_code, 404)

                scan_res = await client.post('/scan', json={'target': '10.0.0.0/24'}, headers={'Authorization': f'Bearer {token}'})
                self.assertEqual(scan_res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
