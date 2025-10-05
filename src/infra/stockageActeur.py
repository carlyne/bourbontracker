from __future__ import annotations

import logging

from sqlalchemy import select

from src.infra.models import Acteur, Organe
from src.infra._baseStockage import _BaseStockage

logger = logging.getLogger(__name__)

class StockageActeur(_BaseStockage):
    def __init__(self):
        super().__init__(
            nom_dossier_zip="acteurs.zip",
            nom_dossier="acteur",
            url= (
                "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
                "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
            )
        )

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
        
    def mettre_a_jour_et_enregistrer_acteurs(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            total_acteurs = self._enregistrer_depuis_dossier(session, Acteur, batch_size=1000)
            session.commit()
        return total_acteurs
