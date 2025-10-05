import json
import logging

from src.infra.models import Organe
from src.infra._baseStockage import _BaseStockage

logger = logging.getLogger(__name__)

class MettreAJourStockOrganes(_BaseStockage):
    def __init__(self):
        super().__init__(
            nom_dossier_zip="acteurs.zip",
            nom_dossier="organe",
            url= (
                "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
                "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
            )
        )

        self._mettre_a_jour_stock()

    def _mettre_a_jour_stock(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            total_organes = self._enregistrer_depuis_dossier(session, Organe, batch_size=1000)
            session.commit()
        return total_organes
