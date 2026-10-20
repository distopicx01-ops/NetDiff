from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from database.motor.eng import Base

class Operation(Base):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True)
    kind = Column(String, nullable=False)
    target = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
