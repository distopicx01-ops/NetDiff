import asyncio
from datetime import datetime

from sqlalchemy import select

from backend.models.device import Device
from backend.models.event import Event
from backend.models.operation import Operation
from backend.models.track import Track
from CLI.src.scanner.diff import compare_scans
from CLI.src.scanner.nmap_scan import scan_network
from CLI.src.scanner.snapshots import load_latest_snapshot, save_snapshot
from tools import load


def add_event(db, kind, ip="", detail=""):
    db.add(Event(kind=kind, ip=ip, detail=detail))


async def save_devices(db, devices, operation_id):
    now = datetime.now()
    for ip, info in devices.items():
        result = await db.execute(select(Device).filter_by(ip=ip))
        device = result.scalars().first()
        if device is None:
            device = Device(ip=ip, hostname=info["hostname"])
            db.add(device)
            await db.flush()
        device.hostname = info["hostname"]
        device.last_seen = now
        ports = ",".join(str(port) for port in info["ports"])
        db.add(Track(device_id=device.id, operation_id=operation_id, open_ports=ports))


def save_events(db, old, new, result):
    black = load("black-list")
    white = load("white-list")

    if old is None:
        add_event(db, "first_scan", detail=f"{len(new)} dispositivos")
        return

    for ip in result["new"]:
        if white.contains(ip):
            continue
        add_event(db, "new_device", ip, new[ip]["hostname"])
        if black.contains(ip):
            add_event(db, "blacklist_alert", ip, "IP de la lista negra aparecio")
    for ip in result["removed"]:
        add_event(db, "removed_device", ip)
    for ip, change in result["ports"].items():
        add_event(db, "ports_changed", ip, f"abiertos={change['opened']} cerrados={change['closed']}")


async def run_check(db, target):
    devices = await asyncio.to_thread(scan_network, target)
    old = load_latest_snapshot()
    save_snapshot(devices)
    result = compare_scans(old or {}, devices)

    operation = Operation(kind="monitor", target=target)
    db.add(operation)
    await db.flush()

    await save_devices(db, devices, operation.id)
    save_events(db, old, devices, result)
    await db.commit()
    return result
