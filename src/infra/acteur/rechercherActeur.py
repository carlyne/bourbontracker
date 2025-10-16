from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.models import ActeurModel, ActeurModel, MandatModel, OrganeModel, OrganeModel

logger = logging.getLogger(__name__)

class RechercherActeur(_BaseConnexionBdd):
    def __init__(self):
        super().__init__()
        
    def recuperer_acteur_par_uid(self, uid: str) -> tuple[ActeurModel | None, list[OrganeModel]]:
        """Récupère un acteur V2 avec ses mandats, collaborateurs, suppléants et organes associés."""

        with self.SessionLocal() as session:
            acteur = session.execute(
                select(ActeurModel)
                .options(
                    selectinload(ActeurModel.mandats)
                    .options(
                        selectinload(MandatModel.collaborateurs),
                        selectinload(MandatModel.suppleants),
                        joinedload(MandatModel.organe),
                    )
                )
                .where(ActeurModel.uid == uid)
            ).scalar_one_or_none()

            if acteur is None:
                return None, []

            organes_uniques: dict[str, OrganeModel] = {}
            for mandat in acteur.mandats:
                if mandat.organe is not None and mandat.organe.uid not in organes_uniques:
                    organes_uniques[mandat.organe.uid] = mandat.organe

            return acteur, list(organes_uniques.values())
