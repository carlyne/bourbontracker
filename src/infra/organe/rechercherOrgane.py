from __future__ import annotations

import logging

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.models import Organe

logger = logging.getLogger(__name__)

class RechercherOrgane(_BaseConnexionBdd):
    def __init__(self):
        super().__init__()

    def recuperer_organe_par_uid(self, uid: str) -> Organe | None:
        with self.SessionLocal() as session:
            return session.get(Organe, uid)