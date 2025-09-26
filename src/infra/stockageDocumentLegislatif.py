import logging
import os
from datetime import datetime, date as date_type
from pathlib import Path
import json

from src.infra.infrastructureException import LectureException
from src.infra.typeFiltrage import TypeFiltrage
from src.infra._baseStockage import _BaseStockage

logger = logging.getLogger(__name__)

class StockageDocumentLegislatif(_BaseStockage):
    
    def __init__(self):
        super().__init__(
            nom_dossier_zip="dossier_legislatifs.zip",
            nom_dossier="document",
            url= "http://data.assemblee-nationale.fr/static/openData/repository/17/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip"
    )
    
    def recuperer_documents_legislatifs_par_date(
            self, 
            date: date_type | None,
            type_filtrage: TypeFiltrage = TypeFiltrage.jour
            ) -> list[dict]:
        
        dossier = Path(self.chemin_dossier_dezippé)

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

