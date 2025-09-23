import shutil
import zipfile
import requests
import logging
import os
import json
from pathlib import Path

from src.infra.infrastructureException import TelechargementException, LectureException

class StockageDeputeEnExercice:
    def __init__(self):
        self.cheminRacine = os.path.abspath("docs_acteurs")
        os.makedirs(self.cheminRacine, exist_ok=True)
        self.cheminZipTemporaire = os.path.join(self.cheminRacine, "acteurs.zip")
        self.cheminDossierActeur = os.path.join(self.cheminRacine, "acteur")
        self.url = (
            "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
            "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
        )

    def mettre_a_jour_stock_acteurs(self):
        try:
            self._telecharger(self.url, self.cheminZipTemporaire)
            self._dezipper_acteurs()
        except Exception as e:
            logging.error("Erreur lors du traitement du ZIP acteurs : %s", e, exc_info=True)
            raise TelechargementException("Impossible de traiter le ZIP des acteurs") from e

    def _telecharger(self, url, dest):
        logging.info("Téléchargement ZIP acteurs -> %s", dest)
        with requests.get(url, stream=True, timeout=(5, 60)) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)

    def _dezipper_acteurs(self):
        logging.info("Extraction des fichiers 'json/acteur/' -> %s", self.cheminDossierActeur)
        os.makedirs(self.cheminDossierActeur, exist_ok=True)
        with zipfile.ZipFile(self.cheminZipTemporaire, "r") as zf:
            for name in zf.namelist():
                if name.startswith("json/acteur/"):
                    dest = os.path.join(self.cheminDossierActeur, name[len("json/acteur/"):])
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with zf.open(name) as src, open(dest, "wb") as out:
                        shutil.copyfileobj(src, out)

    def lire_acteur_par_uid(self, uid: str | None = None) -> tuple[dict, str]:
        dossier = Path(self.cheminDossierActeur)
        if not dossier.exists():
            raise LectureException("Le dossier des acteurs est introuvable")

        try:
            fichiers = sorted(dossier.rglob("*.json"), key=lambda p: p.as_posix())
            if not fichiers:
                raise LectureException("Aucun fichier acteur n'a été trouvé")
            if uid:
                for p in fichiers:
                    with p.open("r", encoding="utf-8") as f:
                        data = json.load(f)   # json stdlib
                        if data.get("acteur", {}).get("uid", {}).get("#text") == uid:
                            return data, str(p)
                raise LectureException(f"Aucun acteur avec uid='{uid}'")
            with fichiers[0].open("r", encoding="utf-8") as f:
                return json.load(f), str(fichiers[0])
        except LectureException:
            raise
        except Exception as e:
            logging.error("Erreur lecture JSON acteur : %s", e, exc_info=True)
            raise LectureException("Impossible de lire un acteur") from e

