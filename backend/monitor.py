import asyncio
from datetime import datetime
from sqlalchemy import select
from backend.models.device import Device
from backend.models.event import Event
from backend.models.operation import Operation
from backend.models.track import Track
from backend.redis_cache import publish_event, cache_set
from CLI.src.scanner.diff import compare_scans
from CLI.src.scanner.nmap_scan import scan_network
from CLI.src.scanner.snapshots import load_latest_snapshot, save_snapshot
from tools import load

async def add_event(db, kind, ip='', detail=''):
    event = Event(kind=kind, ip=ip, detail=detail)
    db.add(event)
    await publish_event('netdiff:events', {'kind': kind, 'ip': ip, 'detail': detail})

async def save_devices(db, devices, operation_id):
    now = datetime.now()
    for ip, info in devices.items():
        stmt = select(Device).filter_by(ip=ip)
        res = await db.execute(stmt)
        device = res.scalars().first()
        if device is None:
            device = Device(ip=ip, hostname=info['hostname'])
            db.add(device)
            await db.flush()
        device.hostname = info['hostname']
        device.last_seen = now
        ports = ','.join(str(p) for p in info['ports'])
        db.add(Track(device_id=device.id, operation_id=operation_id, open_ports=ports))

async def save_events(db, old, new, result):
    black = load('black-list')
    white = load('white-list')
    if old is None:
        await add_event(db, 'first_scan', detail=f'{len(new)} dispositivos')
        return
    for ip in result['new']:
        if white.contains(ip):
            continue
        await add_event(db, 'new_device', ip, new[ip]['hostname'])
        if black.contains(ip):
            await add_event(db, 'blacklist_alert', ip, 'IP de lista negra detectada')
    for ip in result['removed']:
        await add_event(db, 'removed_device', ip)
    for ip, change in result['ports'].items():
        await add_event(db, 'ports_changed', ip, f"abiertos={change['opened']} cerrados={change['closed']}")

async def run_check(db, target):
    devices = scan_network(target)
    old = load_latest_snapshot()
    save_snapshot(devices)
    await cache_set('netdiff:latest_snapshot', devices, expire=600)
    result = compare_scans(old or {}, devices)
    operation = Operation(kind='monitor', target=target)
    db.add(operation)
    await db.flush()
    await save_devices(db, devices, operation.id)
    await save_events(db, old, devices, result)
    await db.commit()
    return result
