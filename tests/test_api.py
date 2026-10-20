import os
import tempfile
import unittest
from unittest import mock

import httpx

_tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
os.environ["DATABASE"] = f"sqlite+aiosqlite:///{_tmp.name}/test.db"
os.environ["JWT_SECRET"] = "test-secret-key-with-at-least-32-bytes-long"

from backend.api import app
from backend.monitor import run_check
from database.motor.eng import AsyncSessionLocal, Base, engine, init_db

FIRST = {"10.0.0.1": {"hostname": "router", "ports": [80]}}
SECOND = {
    "10.0.0.1": {"hostname": "router", "ports": [80, 443]},
    "10.0.0.9": {"hostname": "nuevo", "ports": [135, 445]},
}


def fake_scan(devices, previous):
    return (
        mock.patch("backend.monitor.scan_network", return_value=devices),
        mock.patch("backend.monitor.save_snapshot"),
        mock.patch("backend.monitor.load_latest_snapshot", return_value=previous),
    )


class TestApi(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await init_db()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await init_db()
        transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=transport, base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def run_scan(self, devices, previous):
        patches = fake_scan(devices, previous)
        with patches[0], patches[1], patches[2]:
            async with AsyncSessionLocal() as db:
                return await run_check(db, "10.0.0.0/24")

    async def test_monitor_and_queries(self):
        self.assertEqual((await self.client.get("/health")).json(), {"ok": True})

        await self.run_scan(FIRST, None)
        result = await self.run_scan(SECOND, FIRST)
        self.assertEqual(result["new"], ["10.0.0.9"])

        status = (await self.client.get("/status")).json()
        self.assertEqual(status["devices"], 2)
        self.assertEqual(status["operations"], 2)
        self.assertEqual(status["target"], "10.0.0.0/24")

        devices = {d["ip"]: d for d in (await self.client.get("/devices")).json()}
        self.assertEqual(devices["10.0.0.9"]["os_guess"], "Windows")
        self.assertEqual(devices["10.0.0.1"]["open_ports"], [80, 443])

        kinds = [e["kind"] for e in (await self.client.get("/events")).json()]
        self.assertIn("first_scan", kinds)
        self.assertIn("new_device", kinds)
        self.assertIn("ports_changed", kinds)

        only_new = (await self.client.get("/events?kind=new_device")).json()
        self.assertEqual(len(only_new), 1)

        detail = (await self.client.get("/devices/10.0.0.1")).json()
        self.assertEqual(len(detail["history"]), 2)
        self.assertEqual((await self.client.get("/devices/1.2.3.4")).status_code, 404)
        self.assertEqual(len((await self.client.get("/operations")).json()), 2)

    async def test_auth_and_scan_permissions(self):
        creds = {"username": "admin1", "password": "supersecret1"}
        first = await self.client.post("/auth/register", json=creds)
        self.assertEqual(first.status_code, 201)
        admin_token = first.json()["access_token"]

        again = await self.client.post("/auth/register", json=creds)
        self.assertEqual(again.status_code, 409)

        viewer = await self.client.post(
            "/auth/register", json={"username": "viewer1", "password": "supersecret1"}
        )
        viewer_token = viewer.json()["access_token"]

        bad = await self.client.post(
            "/auth/login", json={"username": "admin1", "password": "wrong-password"}
        )
        self.assertEqual(bad.status_code, 401)
        good = await self.client.post("/auth/login", json=creds)
        self.assertEqual(good.status_code, 200)

        body = {"target": "10.0.0.0/24"}
        self.assertEqual((await self.client.post("/scan", json=body)).status_code, 401)

        as_viewer = await self.client.post(
            "/scan", json=body, headers={"Authorization": f"Bearer {viewer_token}"}
        )
        self.assertEqual(as_viewer.status_code, 403)

        patches = fake_scan(SECOND, None)
        with patches[0], patches[1], patches[2]:
            as_admin = await self.client.post(
                "/scan", json=body, headers={"Authorization": f"Bearer {admin_token}"}
            )
        self.assertEqual(as_admin.status_code, 200)

    async def test_scan_rejects_nmap_options(self):
        register = await self.client.post(
            "/auth/register", json={"username": "admin2", "password": "supersecret2"}
        )
        token = register.json()["access_token"]

        res = await self.client.post(
            "/scan",
            json={"target": "-iL /etc/passwd"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(res.status_code, 422)


if __name__ == "__main__":
    unittest.main()
