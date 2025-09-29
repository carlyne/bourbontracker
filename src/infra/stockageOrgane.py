import json
import logging

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
        chemin_fichier = (self.chemin_dossier_dezippé / uid).with_suffix(".json")

        if not chemin_fichier.exists():
            return None
        
        with chemin_fichier.open("r", encoding="utf-8") as fichier:
            return json.load(fichier)
