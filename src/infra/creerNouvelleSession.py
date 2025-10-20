from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker, 
    Session as SessionType
)

from src.settings import settings

engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

def creer_nouvelle_session() -> SessionType:
    """
    Fournit une nouvelle session liée à l’engine configuré.
    """
    return SessionLocal()
