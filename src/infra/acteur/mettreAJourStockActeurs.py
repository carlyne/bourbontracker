from __future__ import annotations

import logging

from src.infra.models import Acteur
from src.infra._baseStockage import _BaseStockage

logger = logging.getLogger(__name__)

class MettreAJourStockActeurs(_BaseStockage):
    def __init__(self):
        super().__init__(
            nom_dossier_zip="acteurs.zip",
            nom_dossier="acteur",
            url= (
                "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
                "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
            )
        )

        self._mettre_a_jour_stock()
        
    def _mettre_a_jour_stock(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            try:
                total_acteurs = self._enregistrer_depuis_dossier(session, Acteur, batch_size=100)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception("Rollback de la transaction en raison d'une erreur lors de la mise à jour des acteurs")
                raise
        return total_acteurs
