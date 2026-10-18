from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.motor.eng import Base


class Event(Base):
    """Un cambio detectado por el demonio.

    kind puede ser: first_scan, new_device, removed_device,
    ports_changed, blacklist_alert
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    kind = Column(String, nullable=False)
    ip = Column(String, default="")
    detail = Column(String, default="")
    created_at = Column(DateTime, default=datetime.now)
