from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import settings 

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase): # SQLAlchems System um Python-Klassen mit Datenbanktabellen zu verknüpfen -> Diese Klasse repräsentiert eine Tabelle
    pass
