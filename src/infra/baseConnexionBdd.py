from sqlalchemy.orm import Session

from src.infra.creerNouvelleSession import creer_nouvelle_session

class BaseConnexionBdd:
    def __init__(self) -> None:
        self._nouvelle_session = creer_nouvelle_session

    def ouvrir_session(self) -> Session:
        return self._nouvelle_session()