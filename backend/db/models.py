from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone
from backend.db.database import Base
from backend.db.encrypted_type import EncryptedString

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    spotify_user_id = Column(String, unique=True, nullable=False)
    access_token = Column(EncryptedString)
    refresh_token = Column(EncryptedString)
    token_expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
class Analysis(Base):
    __tablename__ = "analysis"
    id =  Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    result = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
class Chunks(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)
    source = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    # Metadaten fürs Hybrid-Retrieval: lexikalisch getaggte MUSIC-Dimensionen und Big-Five-Traits
    # (befüllt beim Ingest via backend.rag.chunk_tagging). Ein Chunk kann zu mehreren gehören
    # oder zu keiner (dann leere Liste) -> Postgres-ARRAY, filterbar per "wert = ANY(spalte)".
    dimensions = Column(ARRAY(String), nullable=False, default=list)
    traits = Column(ARRAY(String), nullable=False, default=list)