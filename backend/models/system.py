from sqlalchemy import Column, ForeignKey, Integer, String
from database.motor.eng import Base

class System(Base):
    __tablename__ = 'systems'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    device_id = Column(Integer, ForeignKey('devices.id'))
