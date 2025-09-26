import shutil
import zipfile
import requests
import json
import logging
from pathlib import Path
import tempfile
from typing import BinaryIO

from src.infra.infrastructureException import MiseAJourStockException

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

    def mettre_a_jour(self):
        try:
            logging.debug("Mise à jour des fichiers acteur vers : %s", self.chemin_acteur)
            self._telecharger()
            self._dezipper()
        except Exception as e:
            logging.error("Erreur lors de la mise à jour des données acteur : %s", e, exc_info=True)
            raise MiseAJourStockException("Impossible de récupérer les données à jour des acteurs") from e
        
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
        
    # --- Private functions

    def _telecharger(self) -> Path:
        self.chemin_zip.parent.mkdir(parents=True, exist_ok=True)

        logging.debug("Téléchargement du dossier '.zip' des acteurs vers : %s", self.chemin_zip)

        chemin_temporaire = self._telecharger_dans_un_chemin_temporaire(self.chemin_zip)
        chemin_temporaire.replace(self.chemin_zip)
    
    def _dezipper(self):
        prefixe = "json/acteur/"
        self.chemin_acteur.mkdir(parents=True, exist_ok=True)

        fichiers_extraits: list[Path] = []
        logging.debug("Extraction des fichiers '.zip' des acteurs '%s*' vers %s", prefixe, self.chemin_acteur)

        with zipfile.ZipFile(self.chemin_zip, "r") as fichier_zip:
            for info in fichier_zip.infolist():
                nom_fichier = info.filename
                if not nom_fichier.startswith(prefixe):
                    continue

                if info.is_dir():
                    (self.chemin_acteur / nom_fichier[len(prefixe):]).mkdir(parents=True, exist_ok=True)
                    continue

                fichier_extrait = (self.chemin_acteur / nom_fichier[len(prefixe):]).resolve()
                fichier_extrait.parent.mkdir(parents=True, exist_ok=True)

                with fichier_zip.open(info, "r") as source, fichier_extrait.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

                fichiers_extraits.append(fichier_extrait)
        
        return fichiers_extraits

    def _telecharger_dans_un_chemin_temporaire(self, destination: Path) -> Path:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
            chemin_temporaire = Path(tmp.name)
            logging.debug("Ecriture du dossier '.zip' des acteurs dans un chemin temporaire : %s", chemin_temporaire)
            self._executer_requete_telechargement_dossier_zip(tmp)
        return chemin_temporaire

    def _executer_requete_telechargement_dossier_zip(self, tmp: BinaryIO):
        with requests.get(self.url, stream=True, timeout=(5, 30)) as reponse:
            logging.debug("Requête de téléchargement du dossier '.zip' des acteurs : %s %s", reponse.request.method, reponse.url)
            reponse.raise_for_status()
            for chunk in reponse.iter_content(chunk_size=256 * 1024):
                if chunk:
                    tmp.write(chunk)
