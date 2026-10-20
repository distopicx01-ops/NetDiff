from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database.motor.eng import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='viewer')
    created_at = Column(DateTime, default=datetime.now)
