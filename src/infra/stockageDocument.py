from __future__ import annotations
import logging
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import json

from src.infra.infrastructureException import LectureException
from src.infra._baseStockage import _BaseStockage

logger = logging.getLogger(__name__)

class StockageDocument(_BaseStockage):
    
    def __init__(self):
        super().__init__(
            nom_dossier_zip="dossier_legislatifs.zip",
            nom_dossier="document",
            url= "http://data.assemblee-nationale.fr/static/openData/repository/17/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip"
    )
    
    def recuperer_documents_recents(self) -> list[dict]:
        fuseau_horaire = ZoneInfo("Europe/Paris")      
        date_du_jour = datetime.now(fuseau_horaire).date()

        trois_jour_avant_date_du_jour = date_du_jour - timedelta(days=3)
        trois_jours_après_date_du_jour = date_du_jour + timedelta(days=3)

        documents_dict: list[dict] = []

        for fichier in self._iterer_dans_tous_le_dossier(self.chemin_dossier_dezippé):
            try:
                with fichier.open("r", encoding="utf-8") as document_json:
                    document_dict = json.load(document_json)

                date_document = self._extraire_date_document(document_dict, fuseau_horaire=fuseau_horaire)
                if date_document is None:
                    continue

                if trois_jour_avant_date_du_jour <= date_document <= trois_jours_après_date_du_jour:
                    documents_dict.append(document_dict)

            except Exception as e:
                logger.exception("Fichier JSON illisible ou invalide: %s", fichier)
                raise LectureException ("Impossible de récupérer le document %s", self.chemin_dossier_dezippé) from e

        return documents_dict

    # --- Private Functions

    @staticmethod
    def _iterer_dans_tous_le_dossier(chemin_racine: Path):
        if not chemin_racine.exists():
            return []
        for fichier in chemin_racine.rglob("*.json"):
            if fichier.is_file():
                yield fichier

    @staticmethod
    def _extraire_date_document(document_json: dict, fuseau_horaire: ZoneInfo) -> None | datetime.date:
        chrono = (
            document_json.get("document", {})
                   .get("cycleDeVie", {})
                   .get("chrono", {})
        )
        document_dates = [
            chrono.get("dateCreation"),
            chrono.get("dateDepot"),
            chrono.get("datePublication"),
            chrono.get("datePublicationWeb"),
        ]

        for document_date in document_dates:
            if not document_date:
                continue
            date_time = StockageDocument._parse_isoaware(document_date)
            if date_time is None:
                continue
            return date_time.astimezone(fuseau_horaire).date()

        return None

    @staticmethod
    def _parse_isoaware(s: str) -> None | datetime:
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            return datetime.fromisoformat(s)
        except ValueError:
            logger.debug("Chaîne ISO invalide: %s", s)
            return None
    
    

