from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from backend.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    spotify_user_id = Column(String, unique=True, nullable=False)
    access_token = Column(String)
    refresh_token = Column(String, unique=True)
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Analysis(Base):
    __tablename__ = "analysis"
    id =  Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    result = Column(JSONB, nullable=False)
    created_at =Column(DateTime, default=datetime.utcnow)