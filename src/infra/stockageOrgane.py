import json
import logging

from src.infra.models import Organe
from src.infra._baseStockage import _BaseStockage

logger = logging.getLogger(__name__)

class StockageOrgane(_BaseStockage):
    def __init__(self):
        super().__init__(
            nom_dossier_zip="acteurs.zip",
            nom_dossier="organe",
            url= (
                "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
                "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
            )
        )

    def recuperer_organe_par_uid(self, uid: str) -> dict | None:
        logger.debug("Récupération de l'organe avec uid : %s",uid)
        chemin_fichier = (self.dossier_dezippé / uid).with_suffix(".json")

        if not chemin_fichier.exists():
            return None
        
        with chemin_fichier.open("r", encoding="utf-8") as fichier:
            return json.load(fichier)

    def mettre_a_jour_et_enregistrer_organes(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            total_organes = self._enregistrer_depuis_dossier(session, Organe, batch_size=1000)
            session.commit()
        return total_organes
