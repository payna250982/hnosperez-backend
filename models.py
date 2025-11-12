from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey 
from sqlalchemy.orm import relationship 
from datetime import datetime 
from database import Base 
 
class User(Base): 
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True, index=True) 
    username = Column(String, unique=True, index=True) 
    password_hash = Column(String) 
    is_admin = Column(Boolean, default=False) 
    records = relationship("WorkRecord", back_populates="user") 
 
class WorkRecord(Base): 
    __tablename__ = "records" 
    id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(Integer, ForeignKey("users.id")) 
    start_time = Column(DateTime, default=datetime.utcnow) 
    end_time = Column(DateTime, nullable=True) 
    user = relationship("User", back_populates="records") 
