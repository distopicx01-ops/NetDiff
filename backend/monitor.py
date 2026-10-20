from backend.models.device import Device
from backend.models.event import Event
from backend.models.operation import Operation
from backend.models.track import Track
from CLI.src.scanner.diff import compare_scans
from CLI.src.scanner.nmap_scan import scan_network
from CLI.src.scanner.snapshots import load_latest_snapshot, save_snapshot
from tools import load
from datetime import datetime

def add_event(db, kind, ip='', detail=''):
    db.add(Event(kind=kind, ip=ip, detail=detail))

def save_devices(db, devices, operation_id):
    now = datetime.now()
    for ip, info in devices.items():
        device = db.query(Device).filter_by(ip=ip).first()
        if device is None:
            device = Device(ip=ip, hostname=info['hostname'])
            db.add(device)
            db.flush()
        device.hostname = info['hostname']
        device.last_seen = now
        ports = ','.join((str(p) for p in info['ports']))
        db.add(Track(device_id=device.id, operation_id=operation_id, open_ports=ports))

def save_events(db, old, new, result):
    black = load('black-list')
    white = load('white-list')
    if old is None:
        add_event(db, 'first_scan', detail=f'{len(new)} dispositivos')
        return
    for ip in result['new']:
        if white.contains(ip):
            continue
        add_event(db, 'new_device', ip, new[ip]['hostname'])
        if black.contains(ip):
            add_event(db, 'blacklist_alert', ip, 'IP de la lista negra apareció')
    for ip in result['removed']:
        add_event(db, 'removed_device', ip)
    for ip, change in result['ports'].items():
        add_event(db, 'ports_changed', ip, f"abiertos={change['opened']} cerrados={change['closed']}")

def run_check(db, target):
    devices = scan_network(target)
    old = load_latest_snapshot()
    save_snapshot(devices)
    result = compare_scans(old or {}, devices)
    operation = Operation(kind='monitor', target=target)
    db.add(operation)
    db.flush()
    save_devices(db, devices, operation.id)
    save_events(db, old, devices, result)
    db.commit()
    return result
