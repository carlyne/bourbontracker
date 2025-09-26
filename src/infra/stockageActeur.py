import shutil
import zipfile
import requests
import os
import json
import logging
from pathlib import Path

from src.infra.infrastructureException import TelechargementException

class StockageActeur:
    def __init__(self):
        self.chemin_racine: Path = Path("docs").resolve()
        self.chemin_racine.mkdir(parents=True, exist_ok=True)
        self.chemin_zip: Path = self.chemin_racine / "acteurs.zip"
        self.chemin_acteur: Path = self.chemin_racine / "acteur"
        self.url: str = (
            "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
            "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
        )

    def mettre_a_jour_stock_acteurs(self):
        try:
            self._telecharger_fichiers(self.url, self.chemin_zip)
            self._dezipper_fichiers()
        except Exception as e:
            logging.error("Erreur lors du traitement du ZIP acteurs : %s", e, exc_info=True)
            raise TelechargementException("Impossible de traiter le ZIP des acteurs") from e
        
    def lire_acteur_par_ref(self, acteur_ref: str) -> dict | None:
        p = Path(self.chemin_acteur) / f"{acteur_ref}.json"
        if not p.is_file():
            logging.warning("Fichier acteur introuvable: %s", p)
            return None
        try:
            with p.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            logging.exception("Impossible de lire le JSON acteur %s: %s", p, e)
            return None

    def _telecharger_fichiers(self, url, dest):
        logging.info("Téléchargement ZIP acteurs -> %s", dest)
        with requests.get(url, stream=True, timeout=(5, 60)) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)

    def _dezipper_fichiers(self):
        logging.info("Extraction des fichiers 'json/acteur/' -> %s", self.chemin_acteur)
        os.makedirs(self.chemin_acteur, exist_ok=True)
        with zipfile.ZipFile(self.chemin_zip, "r") as zf:
            for name in zf.namelist():
                if name.startswith("json/acteur/"):
                    dest = os.path.join(self.chemin_acteur, name[len("json/acteur/"):])
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with zf.open(name) as src, open(dest, "wb") as out:
                        shutil.copyfileobj(src, out)

