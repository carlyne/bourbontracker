import shutil
import zipfile
import requests
import logging
import json
import tempfile
import os

from pathlib import Path
from typing import BinaryIO, Iterator

from src.infra.baseConnexionBdd import BaseConnexionBdd
from src.infra.infrastructureException import MiseAJourStockException

logger = logging.getLogger(__name__)

class _BaseStockage(BaseConnexionBdd):
    def __init__(
            self, 
            nom_dossier_zip: str, 
            nom_dossier: str, 
            url: str
    ) -> None:
        
        super().__init__()

        self.nom_dossier: str = nom_dossier
        self.chemin_racine: Path = self._initialiser_chemin_racine()

        self.chemin_zip: Path = self.chemin_racine / nom_dossier_zip
        self.dossier_dezippé: Path = self.chemin_racine / nom_dossier

        self.url: str = url
    
    def vider_dossier_racine(self) -> None:
        base = Path(self.chemin_racine).resolve()
        logger.info("Réinitialisation de '%s' (suppression + recréation)", base)
        try:
            if base.exists() and base.is_dir() and base.name == "docs":
                try:
                    shutil.rmtree(base)
                except Exception:
                    logger.exception("Suppression de %s échouée", base)
                    raise
                base.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.exception("Réinitialisation de %s échouée", base)

    # --- Private functions

    def _initialiser_chemin_racine(self) -> Path:
        chemin_configuré = os.environ.get("STOCKAGE_RACINE", "docs")
        chemin = Path(chemin_configuré)

        if not chemin.is_absolute():
            chemin = Path.cwd() / chemin

        try:
            chemin.mkdir(parents=True, exist_ok=True)
            return chemin
        except PermissionError:
            chemin_temporaire = Path(tempfile.gettempdir()) / chemin.name
            chemin_temporaire.mkdir(parents=True, exist_ok=True)
            logger.warning(
                "Impossible de créer le dossier %s (PermissionError). Utilisation du dossier temporaire %s.",
                chemin,
                chemin_temporaire,
            )
            return chemin_temporaire


    def _mettre_a_jour(self) -> list[Path]:
        try:
            logger.debug("Mise à jour du dossier %s", self.dossier_dezippé)
            self._telecharger_dossier_zip()
            return self._dezipper_fichiers()
        except Exception as e:
            logger.error("Erreur lors de la mise à jour des données : %s", e, exc_info=True)
            message = ( f"Impossible de récupérer les données à jour du dossier {self.dossier_dezippé} : {e}")
            
            raise MiseAJourStockException(message) from e
        
    def _telecharger_dossier_zip(self):
        self.chemin_zip.parent.mkdir(parents=True, exist_ok=True)

        logger.debug("Téléchargement du dossier '.zip' vers : %s", self.chemin_zip)

        chemin_temporaire = self._telecharger_dans_un_chemin_temporaire(self.chemin_zip)
        chemin_temporaire.replace(self.chemin_zip)
    
    def _dezipper_fichiers(self) -> list[Path]:
        prefixe = "json/" + self.nom_dossier + "/"
        self.dossier_dezippé.mkdir(parents=True, exist_ok=True)

        fichiers_extraits: list[Path] = []
        logger.debug("Extraction des fichiers '.zip' '%s*' vers %s", prefixe, self.dossier_dezippé)

        with zipfile.ZipFile(self.chemin_zip, "r") as fichier_zip:
            for info in fichier_zip.infolist():
                nom_fichier = info.filename
                if not nom_fichier.startswith(prefixe):
                    continue

                if info.is_dir():
                    (self.dossier_dezippé / nom_fichier[len(prefixe):]).mkdir(parents=True, exist_ok=True)
                    continue

                fichier_extrait = (self.dossier_dezippé / nom_fichier[len(prefixe):]).resolve()
                fichier_extrait.parent.mkdir(parents=True, exist_ok=True)

                with fichier_zip.open(info, "r") as source, fichier_extrait.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

                fichiers_extraits.append(fichier_extrait)
        
        return fichiers_extraits
    
    def _telecharger_dans_un_chemin_temporaire(self, destination: Path) -> Path:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
            chemin_temporaire = Path(tmp.name)
            logger.debug("Ecriture du dossier '.zip' %s dans un chemin temporaire : %s", self.nom_dossier, chemin_temporaire)
            self._executer_requete_telechargement_dossier_zip(tmp)
        return chemin_temporaire

    def _executer_requete_telechargement_dossier_zip(self, tmp: BinaryIO):
        with requests.get(self.url, stream=True, timeout=(5, 30)) as reponse:
            logger.debug("Requête de téléchargement du dossier '.zip' %s : %s %s", self.nom_dossier, reponse.request.method, reponse.url)
            reponse.raise_for_status()
            for chunk in reponse.iter_content(chunk_size=256 * 1024):
                if chunk:
                    tmp.write(chunk)
    
    def _itérer_dans_le_dossier_dezippé(self) -> Iterator[Path] :
        if not self.dossier_dezippé.exists():
            # FIXME faire des contrôles en amont ou lever une exception ici si le dossier n'existe pas
            logger.warning("Le dossier %s n'existe pas", self.dossier_dezippé)
            return
        
        # yield : permet de traiter les fichiers en flux continue (méthode utilisée en mode batch)
        yield from (fichier for fichier in self.dossier_dezippé.rglob("*.json") if fichier.is_file())