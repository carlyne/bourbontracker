import shutil
import zipfile
import requests
import logging
from pathlib import Path
import tempfile
from typing import BinaryIO

from src.infra.infrastructureException import MiseAJourStockException

class _BaseStockage:
    def __init__(
            self, 
            nom_dossier_zip: str, 
            nom_dossier: str, 
            url: str
    ) -> None:

        self.nom_dossier: str = nom_dossier
        self.chemin_racine: Path = Path("docs").resolve()
        self.chemin_racine.mkdir(parents=True, exist_ok=True)

        self.chemin_zip: Path = self.chemin_racine / nom_dossier_zip
        self.chemin_dossier_dezippé: Path = self.chemin_racine / nom_dossier

        self.url: str = url

    def mettre_a_jour(self) -> list[Path]:
        try:
            logging.debug("Mise à jour du dossier %s", self.chemin_dossier_dezippé)
            self._telecharger_dossier_zip()
            return self._dezipper_fichiers()
        except Exception as e:
            logging.error("Erreur lors de la mise à jour des données : %s", e, exc_info=True)
            raise MiseAJourStockException("Impossible de récupérer les données à jour du dossier %s", self.chemin_dossier_dezippé) from e
        
    def vider_dossier_racice(self) -> None:
        base = Path(self.chemin_racine).resolve()
        logging.info("Réinitialisation de '%s' (suppression + recréation)", base)
        try:
            if base.exists() and base.is_dir() and base.name == "docs":
                try:
                    shutil.rmtree(base)
                except Exception:
                    logging.exception("Suppression de %s échouée", base)
                    raise
                base.mkdir(parents=True, exist_ok=True)
        except Exception:
            logging.exception("Réinitialisation de %s échouée", base) 

    # --- Private functions

    def _telecharger_dossier_zip(self):
        self.chemin_zip.parent.mkdir(parents=True, exist_ok=True)

        logging.debug("Téléchargement du dossier '.zip' vers : %s", self.chemin_zip)

        chemin_temporaire = self._telecharger_dans_un_chemin_temporaire(self.chemin_zip)
        chemin_temporaire.replace(self.chemin_zip)
    
    def _dezipper_fichiers(self) -> list[Path]:
        prefixe = "json/" + self.nom_dossier + "/"
        self.chemin_dossier_dezippé.mkdir(parents=True, exist_ok=True)

        fichiers_extraits: list[Path] = []
        logging.debug("Extraction des fichiers '.zip' '%s*' vers %s", prefixe, self.chemin_dossier_dezippé)

        with zipfile.ZipFile(self.chemin_zip, "r") as fichier_zip:
            for info in fichier_zip.infolist():
                nom_fichier = info.filename
                if not nom_fichier.startswith(prefixe):
                    continue

                if info.is_dir():
                    (self.chemin_dossier_dezippé / nom_fichier[len(prefixe):]).mkdir(parents=True, exist_ok=True)
                    continue

                fichier_extrait = (self.chemin_dossier_dezippé / nom_fichier[len(prefixe):]).resolve()
                fichier_extrait.parent.mkdir(parents=True, exist_ok=True)

                with fichier_zip.open(info, "r") as source, fichier_extrait.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

                fichiers_extraits.append(fichier_extrait)
        
        return fichiers_extraits
    
    def _telecharger_dans_un_chemin_temporaire(self, destination: Path) -> Path:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
            chemin_temporaire = Path(tmp.name)
            logging.debug("Ecriture du dossier '.zip' %s dans un chemin temporaire : %s", self.nom_dossier, chemin_temporaire)
            self._executer_requete_telechargement_dossier_zip(tmp)
        return chemin_temporaire

    def _executer_requete_telechargement_dossier_zip(self, tmp: BinaryIO):
        with requests.get(self.url, stream=True, timeout=(5, 30)) as reponse:
            logging.debug("Requête de téléchargement du dossier '.zip' %s : %s %s", self.nom_dossier, reponse.request.method, reponse.url)
            reponse.raise_for_status()
            for chunk in reponse.iter_content(chunk_size=256 * 1024):
                if chunk:
                    tmp.write(chunk)