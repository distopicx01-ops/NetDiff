from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from database.motor.eng import Base

class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    operation_id = Column(Integer, ForeignKey('operations.id'))
    open_ports = Column(String, default='')
    seen_at = Column(DateTime, default=datetime.now)
