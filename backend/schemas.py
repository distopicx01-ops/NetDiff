from datetime import datetime
from ipaddress import ip_network

from pydantic import BaseModel, Field, field_validator


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DeviceOut(BaseModel):
    ip: str
    hostname: str = ""
    open_ports: list[int] = []
    os_guess: str = "Desconocido"
    first_seen: datetime | None = None
    last_seen: datetime | None = None


class TrackOut(BaseModel):
    seen_at: datetime | None = None
    open_ports: list[int] = []


class DeviceDetailOut(DeviceOut):
    history: list[TrackOut] = []


class EventOut(BaseModel):
    id: int
    kind: str
    ip: str = ""
    detail: str = ""
    created_at: datetime | None = None


class OperationOut(BaseModel):
    id: int
    kind: str
    target: str
    created_at: datetime | None = None


class StatusOut(BaseModel):
    devices: int
    events: int
    operations: int
    last_scan: datetime | None = None
    target: str | None = None


class ScanRequest(BaseModel):
    target: str

    @field_validator("target")
    @classmethod
    def target_must_be_ip_or_network(cls, value):
        try:
            ip_network(value, strict=False)
        except ValueError:
            raise ValueError("target debe ser una IP o una red, por ejemplo 192.168.1.0/24")
        return value
