from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import (
    create_access_token,
    hash_password,
    require_admin,
    verify_password,
)
from backend.models.device import Device
from backend.models.event import Event
from backend.models.operation import Operation
from backend.models.track import Track
from backend.models.user import User
from backend.monitor import run_check
from backend.schemas import (
    DeviceDetailOut,
    DeviceOut,
    EventOut,
    OperationOut,
    ScanRequest,
    StatusOut,
    TokenOut,
    UserCreate,
    UserLogin,
)
from CLI.src.scanner.snapshots import load_latest_snapshot
from CLI.src.systems import guess_os
from database.motor.eng import get_db, init_db
from tools import load


@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield


app = FastAPI(title="NetDiff API", lifespan=lifespan)


def ports_to_list(text):
    return [int(port) for port in text.split(",")] if text else []


def device_to_dict(device, ports):
    return {
        "ip": device.ip,
        "hostname": device.hostname,
        "open_ports": ports,
        "os_guess": guess_os(ports),
        "first_seen": device.first_seen,
        "last_seen": device.last_seen,
    }


async def last_ports(db, device_id):
    result = await db.execute(
        select(Track).filter_by(device_id=device_id).order_by(Track.id.desc()).limit(1)
    )
    track = result.scalars().first()
    return ports_to_list(track.open_ports) if track else []


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/auth/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(select(User).filter_by(username=body.username))
    if exists.scalars().first():
        raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya existe")

    total = (await db.execute(select(func.count(User.id)))).scalar()
    role = "admin" if total == 0 else "viewer"

    db.add(User(username=body.username, password_hash=hash_password(body.password), role=role))
    await db.commit()
    return {"access_token": create_access_token(body.username, role)}


@app.post("/auth/login", response_model=TokenOut)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter_by(username=body.username))
    user = result.scalars().first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contrasena incorrectos")
    return {"access_token": create_access_token(user.username, user.role)}


@app.get("/status", response_model=StatusOut)
async def get_status(db: AsyncSession = Depends(get_db)):
    last = (
        await db.execute(select(Operation).order_by(Operation.id.desc()).limit(1))
    ).scalars().first()
    return {
        "devices": (await db.execute(select(func.count(Device.id)))).scalar(),
        "events": (await db.execute(select(func.count(Event.id)))).scalar(),
        "operations": (await db.execute(select(func.count(Operation.id)))).scalar(),
        "last_scan": last.created_at if last else None,
        "target": last.target if last else None,
    }


@app.get("/devices", response_model=list[DeviceOut])
async def list_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).order_by(Device.ip))
    return [device_to_dict(d, await last_ports(db, d.id)) for d in result.scalars().all()]


@app.get("/devices/{ip}", response_model=DeviceDetailOut)
async def device_detail(ip: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).filter_by(ip=ip))
    device = result.scalars().first()
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dispositivo no encontrado")

    tracks = await db.execute(
        select(Track).filter_by(device_id=device.id).order_by(Track.id.desc()).limit(20)
    )
    history = [
        {"seen_at": t.seen_at, "open_ports": ports_to_list(t.open_ports)}
        for t in tracks.scalars().all()
    ]
    data = device_to_dict(device, history[0]["open_ports"] if history else [])
    data["history"] = history
    return data


@app.get("/events", response_model=list[EventOut])
async def list_events(limit: int = 50, kind: str = "", db: AsyncSession = Depends(get_db)):
    query = select(Event)
    if kind:
        query = query.filter_by(kind=kind)
    result = await db.execute(query.order_by(Event.id.desc()).limit(limit))
    return result.scalars().all()


@app.get("/operations", response_model=list[OperationOut])
async def list_operations(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Operation).order_by(Operation.id.desc()).limit(limit))
    return result.scalars().all()


@app.get("/snapshot/latest")
async def latest_snapshot():
    return load_latest_snapshot() or {}


@app.get("/lists")
async def lists():
    return {
        "white_list": load("white-list").get_all(),
        "black_list": load("black-list").get_all(),
    }


@app.post("/scan")
async def scan_now(
    body: ScanRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    try:
        result = await run_check(db, body.target)
    except RuntimeError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))
    return {"target": body.target, "diff": result}
