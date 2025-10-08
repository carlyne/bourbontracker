import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import settings

logger = logging.getLogger(__name__)


class _BaseConnexionBdd:
    def __init__(self) -> None:
        self.engine = create_engine(
            settings.database_url,
            future=True,
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )
