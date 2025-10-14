from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.models import Acteur, ActeurV2, Mandat, Organe, OrganeV2

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
        
    def recuperer_acteur_par_uid_v2(self, uid: str) -> tuple[ActeurV2 | None, list[OrganeV2]]:
        """Récupère un acteur V2 avec ses mandats, collaborateurs, suppléants et organes associés."""

        with self.SessionLocal() as session:
            acteur = session.execute(
                select(ActeurV2)
                .options(
                    selectinload(ActeurV2.mandats)
                    .options(
                        selectinload(Mandat.collaborateurs),
                        selectinload(Mandat.suppleants),
                        joinedload(Mandat.organe),
                    )
                )
                .where(ActeurV2.uid == uid)
            ).scalar_one_or_none()

            if acteur is None:
                return None, []

            organes_uniques: dict[str, OrganeV2] = {}
            for mandat in acteur.mandats:
                if mandat.organe is not None and mandat.organe.uid not in organes_uniques:
                    organes_uniques[mandat.organe.uid] = mandat.organe

            return acteur, list(organes_uniques.values())
