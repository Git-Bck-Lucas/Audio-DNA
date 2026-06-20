from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
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
    
class Chunks(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)
    source = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)