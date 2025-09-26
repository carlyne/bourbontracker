import json
from pathlib import Path

from src.infra._baseStockage import _BaseStockage

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

    def recuperer_acteur_par_ref(self, acteur_ref: str) -> dict | None:
        chemin_fichier = self._recuperer_fichier_acteur(acteur_ref)
        with chemin_fichier.open("r", encoding="utf-8") as fichier:
            return json.load(fichier)
        
    # --- Private functions
    
    def _recuperer_fichier_acteur(self, acteur_ref: str) -> Path:
        chemin_fichier = (self.chemin_dossier_dezippé / acteur_ref).with_suffix(".json")
        if not chemin_fichier.exists():
            return None
        return chemin_fichier
