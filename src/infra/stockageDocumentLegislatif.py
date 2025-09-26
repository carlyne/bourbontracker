import shutil
import zipfile
import requests
import logging
import os
from datetime import datetime, date as date_type
from pathlib import Path
import json
from typing import Any

from src.infra.infrastructureException import MiseAJourStockException, LectureException
from src.infra.typeFiltrage import TypeFiltrage

logger = logging.getLogger(__name__)

class StockageDocumentLegislatif:
    def __init__(self):
        self.chemin_racine = os.path.abspath("docs")
        self.chemin_zip_temporaire = os.path.join(self.chemin_racine, "dossier_legislatifs.zip")
        self.chemin_dossier_documents_legislatifs = os.path.join(self.chemin_racine, "documents-legislatifs")
        self.url = "http://data.assemblee-nationale.fr/static/openData/repository/17/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip"
    
    def recuperer_documents_legislatifs_par_date(
            self, 
            date: date_type | None,
            type_filtrage: TypeFiltrage = TypeFiltrage.jour
            ) -> list[dict]:
        dossier = Path(self.chemin_dossier_documents_legislatifs + "/document")

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

    def mettre_a_jour_stock_documents_legislatifs(self):
        try:
            dossier_zip = os.path.basename(self.chemin_zip_temporaire)
            self._telecharger_dossier(self.url, self.chemin_zip_temporaire)
            self._dezipper_dossier_vers_destination(dossier_zip)
        except Exception as e:
            logging.error(f"Erreur lors du téléchargement du dossier zip correspondant aux documents legislatifs : {e}", exc_info=True)
            raise MiseAJourStockException(f"Impossible de traiter le dossier zip correspondant aux documents legislatifs")

    def _telecharger_dossier(self, url, chemin_zip_temporaire):
        logging.info(f"Téléchargement du dossier zip {chemin_zip_temporaire}")
        reponse = requests.get(url, stream=True)
        with open(chemin_zip_temporaire, 'wb') as dossier:
                for chunk in reponse.iter_content(chunk_size=8192):
                        dossier.write(chunk)

    def _dezipper_dossier_vers_destination(self, dossier_zip):
        with zipfile.ZipFile(self.chemin_zip_temporaire, 'r') as dossier:
            logging.info(f"Extraction des fichiers du zip {dossier_zip} dans {self.chemin_dossier_documents_legislatifs}")
            for fichier in dossier.namelist():
                if fichier.startswith('json/'):
                    chemin_de_destination = os.path.join(self.chemin_dossier_documents_legislatifs, fichier[len('json/'):])
                    os.makedirs(os.path.dirname(chemin_de_destination), exist_ok=True)
                    with dossier.open(fichier) as source, open(chemin_de_destination, 'wb') as destination:
                        shutil.copyfileobj(source,destination)

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
