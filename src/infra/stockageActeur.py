import shutil
import zipfile
import requests
import logging
import os
import json
from pathlib import Path

from src.infra.infrastructureException import TelechargementException, LectureException

class StockageActeur:
    def __init__(self):
        self.chemin_racine = os.path.abspath("docs/acteur")
        os.makedirs(self.chemin_racine, exist_ok=True)
        self.chemin_zip_temporaire = os.path.join(self.chemin_racine, "acteurs.zip")
        self.chemin_dossier_acteur = os.path.join(self.chemin_racine, "acteur")
        self.url = (
            "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
            "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
        )

    def mettre_a_jour_stock_acteurs(self):
        try:
            self._telecharger_fichiers(self.url, self.chemin_zip_temporaire)
            self._dezipper_fichiers()
        except Exception as e:
            logging.error("Erreur lors du traitement du ZIP acteurs : %s", e, exc_info=True)
            raise TelechargementException("Impossible de traiter le ZIP des acteurs") from e

    def _telecharger_fichiers(self, url, dest):
        logging.info("Téléchargement ZIP acteurs -> %s", dest)
        with requests.get(url, stream=True, timeout=(5, 60)) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)

    def _dezipper_fichiers(self):
        logging.info("Extraction des fichiers 'json/acteur/' -> %s", self.chemin_dossier_acteur)
        os.makedirs(self.chemin_dossier_acteur, exist_ok=True)
        with zipfile.ZipFile(self.chemin_zip_temporaire, "r") as zf:
            for name in zf.namelist():
                if name.startswith("json/acteur/"):
                    dest = os.path.join(self.chemin_dossier_acteur, name[len("json/acteur/"):])
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with zf.open(name) as src, open(dest, "wb") as out:
                        shutil.copyfileobj(src, out)

    def recuperer_acteur_depuis_uid(self, uid: str | None = None) -> tuple[dict, str]:
        dossier = Path(self.chemin_dossier_acteur)

        if not dossier.exists():
            raise LectureException("Le dossier acteur est introuvable")

        try:
            if uid:
                cible = list(dossier.rglob(f"{uid}.json"))
                if cible:
                    fichier = cible[0]
                    with fichier.open("r", encoding="utf-8") as fichier:
                        return json.load(fichier), str(fichier)

            fichiers = sorted(dossier.rglob("*.json"), key=lambda p: p.as_posix())
            if not fichiers:
                raise LectureException("Aucun fichier acteur n'a été trouvé")

            if uid:
                for fichier in fichiers:
                    with fichier.open("r", encoding="utf-8") as fichier:
                        data = json.load(fichier)
                        if data.get("acteur", {}).get("uid", {}).get("#text") == uid:
                            return data, str(fichier)
                raise LectureException(f"Aucun acteur avec uid='{uid}'")

            with fichiers[0].open("r", encoding="utf-8") as fichier:
                return json.load(fichier), str(fichiers[0])

        except LectureException:
            raise
        except Exception as e:
            logging.exception("Erreur lecture JSON acteur")
            raise LectureException("Impossible de récupérer l'acteur") from e

