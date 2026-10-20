from datetime import datetime
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class DeviceOut(BaseModel):
    ip: str
    hostname: str = ''
    open_ports: list[int] = []
    os_guess: str = 'Desconocido'
    first_seen: datetime | None = None
    last_seen: datetime | None = None

class EventOut(BaseModel):
    id: int
    kind: str
    ip: str = ''
    detail: str = ''
    created_at: datetime | None = None

class StatusOut(BaseModel):
    devices: int
    events: int
    operations: int
    last_scan: datetime | None = None
    target: str | None = None

class ScanRequest(BaseModel):
    target: str
