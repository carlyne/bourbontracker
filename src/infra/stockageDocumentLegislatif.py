import shutil
import zipfile
import requests
import logging
import os
from datetime import datetime, date as date_type
from pathlib import Path
import json
from typing import BinaryIO
import tempfile

from src.infra.infrastructureException import MiseAJourStockException, LectureException
from src.infra.typeFiltrage import TypeFiltrage

logger = logging.getLogger(__name__)

class StockageDocumentLegislatif:
    def __init__(self):
        self.chemin_racine: Path = Path("docs").resolve()
        self.chemin_racine.mkdir(parents=True, exist_ok=True)

        self.chemin_zip: Path = self.chemin_racine / "dossier_legislatifs.zip"
        self.chemin_doc_legislatif: Path = self.chemin_racine / "documents-legislatifs"

        self.url: str = "http://data.assemblee-nationale.fr/static/openData/repository/17/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip"

    def recuperer_documents_legislatifs_par_date(
            self, 
            date: date_type | None,
            type_filtrage: TypeFiltrage = TypeFiltrage.jour
            ) -> list[dict]:
        dossier = Path(self.chemin_doc_legislatif)

        if not dossier.exists():
            logging.warning("Le dossier de documents legislatifs n'existe pas : %s", dossier)
            return []
        try:
            fichiers: list[dict] = []
            with os.scandir(dossier) as contenu_dossier:
                for element in contenu_dossier:
                    if not element.is_file() or not element.name.endswith(".json"):
                        continue
                    try:
                        with open(element.path, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                    except Exception as e:
                        logger.exception("JSON illisible: %s", element.path)
                        continue 
                    uid = data["document"]["uid"]
                    date_fichier = (
                        data.get("document", {})
                            .get("cycleDeVie", {})
                            .get("chrono", {})
                            .get("dateCreation")
                    )
                    if not isinstance(date_fichier, str):
                        logger.warning(
                            "dateCreation non exploitable (type=%s) pour uid=%s, fichier=%s, valeur=%r",
                            type(date_fichier).__name__, uid, element.path, date_fichier
                        )
                        fichiers.append(data)
                        continue
                    try:
                        datetime_fichier = datetime.fromisoformat(date_fichier)
                    except (TypeError, ValueError) as e:
                        logger.warning(
                            "dateCreation invalide ISO pour uid=%s, fichier=%s, valeur=%r, erreur=%s",
                            uid, element.path, date_fichier, e
                        )
                        continue
                    date_creation = datetime_fichier.date()
                    
                    if date is None:
                        fichiers.append(data)
                        continue
                    
                    if type_filtrage == TypeFiltrage.jour:
                        ok = (date_creation == date)

                    elif type_filtrage == TypeFiltrage.semaine:
                        same_month_year = (date_creation.year == date.year and date_creation.month == date.month)
                        delta_days = abs((date_creation - date).days)
                        ok = same_month_year and (delta_days <= 3)

                    elif type_filtrage == TypeFiltrage.mois:
                        ok = (date_creation.year == date.year and date_creation.month == date.month)

                    else:
                        ok = False

                    if ok:
                        fichiers.append(data)
            return fichiers
        except Exception as e:
            logging.error("Erreur lors de la lecture des documents legislatifs : %s", e, exc_info=True)
            raise LectureException("Impossible de lire les documents legislatifs stockés") from e
    def mettre_a_jour(self) -> list[Path]:
        try:
            logging.debug("Mise à jour des fichiers documents legislatifs vers : %s", self.chemin_doc_legislatif)
            self._telecharger_dossier_zip()
            return self._dezipper_fichiers()
        except Exception as e:
            logging.error("Erreur lors de la mise à jour des données documents legislatifs : %s", e, exc_info=True)
            raise MiseAJourStockException("Impossible de récupérer les données à jour des documents legislatifs") from e

    # --- Private Functions
    
    def _telecharger_dossier_zip(self):
        self.chemin_zip.parent.mkdir(parents=True, exist_ok=True)

        logging.debug("Téléchargement du dossier '.zip' des documents legislatif vers : %s", self.chemin_zip)

        chemin_temporaire = self._telecharger_dans_un_chemin_temporaire(self.chemin_zip)
        chemin_temporaire.replace(self.chemin_zip)
    
    def _dezipper_fichiers(self) -> list[Path]:
        prefixe = "json/document/"
        self.chemin_doc_legislatif.mkdir(parents=True, exist_ok=True)

        fichiers_extraits: list[Path] = []
        logging.debug("Extraction des fichiers '.zip' des documents legislatifs '%s*' vers %s", prefixe, self.chemin_doc_legislatif)

        with zipfile.ZipFile(self.chemin_zip, "r") as fichier_zip:
            for info in fichier_zip.infolist():
                nom_fichier = info.filename
                if not nom_fichier.startswith(prefixe):
                    continue

                if info.is_dir():
                    (self.chemin_doc_legislatif / nom_fichier[len(prefixe):]).mkdir(parents=True, exist_ok=True)
                    continue

                fichier_extrait = (self.chemin_doc_legislatif / nom_fichier[len(prefixe):]).resolve()
                fichier_extrait.parent.mkdir(parents=True, exist_ok=True)

                with fichier_zip.open(info, "r") as source, fichier_extrait.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

                fichiers_extraits.append(fichier_extrait)
        
        return fichiers_extraits
    
    def _telecharger_dans_un_chemin_temporaire(self, destination: Path) -> Path:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
            chemin_temporaire = Path(tmp.name)
            logging.debug("Ecriture du dossier '.zip' des documents legislatifs dans un chemin temporaire : %s", chemin_temporaire)
            self._executer_requete_telechargement_dossier_zip(tmp)
        return chemin_temporaire

    def _executer_requete_telechargement_dossier_zip(self, tmp: BinaryIO):
        with requests.get(self.url, stream=True, timeout=(5, 30)) as reponse:
            logging.debug("Requête de téléchargement du dossier '.zip' des documents legislatifs : %s %s", reponse.request.method, reponse.url)
            reponse.raise_for_status()
            for chunk in reponse.iter_content(chunk_size=256 * 1024):
                if chunk:
                    tmp.write(chunk)

    def nettoyer_dossier_docs(self) -> None:
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
