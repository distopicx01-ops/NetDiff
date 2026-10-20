from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.auth import create_access_token, hash_password, verify_password, get_current_user
from backend.models.device import Device
from backend.models.event import Event
from backend.models.operation import Operation
from backend.models.track import Track
from backend.models.user import User
from backend.monitor import run_check
from backend.redis_cache import cache_get, cache_set
from backend.schemas import DeviceOut, EventOut, ScanRequest, StatusOut, TokenOut, UserLogin
from CLI.src.scanner.snapshots import load_latest_snapshot
from CLI.src.systems import guess_os
from database.motor.eng import get_db, init_db
from tools import load

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title='NetDiff API', lifespan=lifespan)

def ports_to_list(text):
    return [int(p) for p in text.split(',')] if text else []

async def last_ports(db: AsyncSession, device_id: int):
    stmt = select(Track).filter_by(device_id=device_id).order_by(Track.id.desc())
    res = await db.execute(stmt)
    track = res.scalars().first()
    return ports_to_list(track.open_ports) if track else []

@app.post('/auth/register', response_model=TokenOut)
async def register(body: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(username=body.username)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail='El usuario ya existe')
    role = 'viewer'
    user = User(username=body.username, password_hash=hash_password(body.password), role=role)
    db.add(user)
    await db.commit()
    token = create_access_token({'sub': body.username, 'role': role})
    return {'access_token': token, 'token_type': 'bearer'}

@app.post('/auth/login', response_model=TokenOut)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(username=body.username)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciales invalidas')
    token = create_access_token({'sub': user.username, 'role': user.role})
    return {'access_token': token, 'token_type': 'bearer'}

@app.get('/health')
async def health():
    return {'ok': True}

@app.get('/status', response_model=StatusOut)
async def get_status(db: AsyncSession = Depends(get_db)):
    cached = await cache_get('netdiff:status')
    if cached:
        return cached
    count_dev = (await db.execute(select(func.count(Device.id)))).scalar() or 0
    count_evt = (await db.execute(select(func.count(Event.id)))).scalar() or 0
    count_ops = (await db.execute(select(func.count(Operation.id)))).scalar() or 0
    stmt_last = select(Operation).order_by(Operation.id.desc())
    last_op = (await db.execute(stmt_last)).scalars().first()
    data = {
        'devices': count_dev,
        'events': count_evt,
        'operations': count_ops,
        'last_scan': last_op.created_at if last_op else None,
        'target': last_op.target if last_op else None
    }
    await cache_set('netdiff:status', data, expire=30)
    return data

@app.get('/devices', response_model=list[DeviceOut])
async def list_devices(db: AsyncSession = Depends(get_db)):
    stmt = select(Device).order_by(Device.ip)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    out = []
    for d in rows:
        ports = await last_ports(db, d.id)
        out.append({
            'ip': d.ip,
            'hostname': d.hostname,
            'open_ports': ports,
            'os_guess': guess_os(ports),
            'first_seen': d.first_seen,
            'last_seen': d.last_seen
        })
    return out

@app.get('/devices/{ip}', response_model=DeviceOut)
async def device_detail(ip: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Device).filter_by(ip=ip)
    res = await db.execute(stmt)
    device = res.scalars().first()
    if device is None:
        raise HTTPException(status_code=404, detail='Dispositivo no encontrado')
    ports = await last_ports(db, device.id)
    return {
        'ip': device.ip,
        'hostname': device.hostname,
        'open_ports': ports,
        'os_guess': guess_os(ports),
        'first_seen': device.first_seen,
        'last_seen': device.last_seen
    }

@app.get('/events', response_model=list[EventOut])
async def list_events(limit: int = 50, kind: str = '', db: AsyncSession = Depends(get_db)):
    stmt = select(Event)
    if kind:
        stmt = stmt.filter_by(kind=kind)
    stmt = stmt.order_by(Event.id.desc()).limit(limit)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return [{'id': e.id, 'kind': e.kind, 'ip': e.ip, 'detail': e.detail, 'created_at': e.created_at} for e in rows]

@app.get('/operations')
async def list_operations(limit: int = 20, db: AsyncSession = Depends(get_db)):
    stmt = select(Operation).order_by(Operation.id.desc()).limit(limit)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return [{'id': o.id, 'kind': o.kind, 'target': o.target, 'created_at': o.created_at} for o in rows]

@app.post('/scan')
async def trigger_scan(req: ScanRequest, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    result = await run_check(db, req.target)
    return {'ok': True, 'target': req.target, 'diff': result}

@app.get('/snapshot/latest')
async def latest_snapshot():
    cached = await cache_get('netdiff:latest_snapshot')
    if cached:
        return cached
    return load_latest_snapshot() or {}

@app.get('/lists')
async def get_lists():
    return {
        'white_list': load('white-list').get_all(),
        'black_list': load('black-list').get_all()
    }
