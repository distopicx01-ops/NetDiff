from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from database.motor.eng import Base

class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True)
    ip = Column(String, unique=True, nullable=False)
    hostname = Column(String, default='')
    first_seen = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now)
