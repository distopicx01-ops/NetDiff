from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.motor.eng import Base


class Operation(Base):
    """Cada vez que el usuario corre un escaneo se guarda una operacion."""

    __tablename__ = "operations"

    id = Column(Integer, primary_key=True)
    kind = Column(String, nullable=False)  # scan, diff, deep, check
    target = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)