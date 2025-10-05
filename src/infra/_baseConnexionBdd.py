import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

class _BaseConnexionBdd:
    def __init__(self) -> None:
        self.engine = create_engine("postgresql+psycopg2://user:pass@localhost:5433/assemblee", future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)