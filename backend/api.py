from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.models.device import Device
from backend.models.event import Event
from backend.models.operation import Operation
from backend.models.track import Track
from CLI.src.scanner.snapshots import load_latest_snapshot
from CLI.src.systems import guess_os
from database.init_db import init_db
from database.motor.eng import get_db
from tools import load
app = FastAPI(title='NetDiff API')
init_db()

def ports_to_list(text):
    return [int(p) for p in text.split(',')] if text else []

def device_to_dict(device, ports):
    return {'ip': device.ip, 'hostname': device.hostname, 'open_ports': ports, 'os_guess': guess_os(ports), 'first_seen': device.first_seen, 'last_seen': device.last_seen}

def last_ports(db, device_id):
    track = db.query(Track).filter_by(device_id=device_id).order_by(Track.id.desc()).first()
    return ports_to_list(track.open_ports) if track else []

@app.get('/health')
def health():
    return {'ok': True}

@app.get('/status')
def status(db: Session=Depends(get_db)):
    last = db.query(Operation).order_by(Operation.id.desc()).first()
    return {'devices': db.query(func.count(Device.id)).scalar(), 'events': db.query(func.count(Event.id)).scalar(), 'operations': db.query(func.count(Operation.id)).scalar(), 'last_scan': last.created_at if last else None, 'target': last.target if last else None}

@app.get('/devices')
def devices(db: Session=Depends(get_db)):
    rows = db.query(Device).order_by(Device.ip).all()
    return [device_to_dict(d, last_ports(db, d.id)) for d in rows]

@app.get('/devices/{ip}')
def device_detail(ip: str, db: Session=Depends(get_db)):
    device = db.query(Device).filter_by(ip=ip).first()
    if device is None:
        raise HTTPException(status_code=404, detail='Dispositivo no encontrado')
    tracks = db.query(Track).filter_by(device_id=device.id).order_by(Track.id.desc()).limit(20)
    history = [{'seen_at': t.seen_at, 'open_ports': ports_to_list(t.open_ports)} for t in tracks]
    data = device_to_dict(device, history[0]['open_ports'] if history else [])
    data['history'] = history
    return data

@app.get('/events')
def events(limit: int=50, kind: str='', db: Session=Depends(get_db)):
    query = db.query(Event)
    if kind:
        query = query.filter_by(kind=kind)
    rows = query.order_by(Event.id.desc()).limit(limit).all()
    return [{'id': e.id, 'kind': e.kind, 'ip': e.ip, 'detail': e.detail, 'created_at': e.created_at} for e in rows]

@app.get('/operations')
def operations(limit: int=20, db: Session=Depends(get_db)):
    rows = db.query(Operation).order_by(Operation.id.desc()).limit(limit).all()
    return [{'id': o.id, 'kind': o.kind, 'target': o.target, 'created_at': o.created_at} for o in rows]

@app.get('/snapshot/latest')
def latest_snapshot():
    return load_latest_snapshot() or {}

@app.get('/lists')
def lists():
    return {'white_list': load('white-list').get_all(), 'black_list': load('black-list').get_all()}
