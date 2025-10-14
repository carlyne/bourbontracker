from __future__ import annotations

import logging

from sqlalchemy import select

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.models import Organe, OrganeV2

logger = logging.getLogger(__name__)

class RechercherOrgane(_BaseConnexionBdd):
    def __init__(self):
        super().__init__()

    def recuperer_organe_par_uid(self, uid: str) -> dict | None:
        with self.SessionLocal() as session: 
            organe_stocké = session.execute(
                select(Organe.payload).where(Organe.uid == uid)
            ).first()

            if organe_stocké is None:
                return {}, []

            organe_payload = organe_stocké[0]

            return organe_payload
        
    def recuperer_organe_par_uid_v2(self, uid: str) -> OrganeV2 | None:
        with self.SessionLocal() as session:
            return session.get(OrganeV2, uid) 