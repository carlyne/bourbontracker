from __future__ import annotations

import logging

from sqlalchemy import select

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.models import Acteur, Organe

logger = logging.getLogger(__name__)

class RechercherActeur(_BaseConnexionBdd):
    def __init__(self):
        super().__init__()

    def recuperer_acteur_par_uid(self, uid: str) -> tuple[dict, list[dict]]:
        """
        Récupère les données d'un Acteur à l'aide de son uid.
        Récupère également les organes associés s'il y en a
        """
        with self.SessionLocal() as session: 
            données_en_base = session.execute(
                select(Acteur.payload, Acteur.organe_refs_jsonb).where(Acteur.uid == uid)
            ).first()

            if données_en_base is None:
                return {}, []

            acteur_payload, organes_refs_json = données_en_base[0], (données_en_base[1] or [])

            organes_refs: list[str] = [organe_ref for organe_ref in organes_refs_json if isinstance(organe_ref, str)]

            if not organes_refs:
                return acteur_payload, []

            organes_payloads: list[dict] = session.execute(
                select(Organe.payload).where(Organe.uid.in_(organes_refs))
            ).scalars().all()

            return acteur_payload, organes_payloads
