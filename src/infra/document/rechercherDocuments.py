from __future__ import annotations

import logging

from sqlalchemy import select, func, text, cast, DATE
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.models import Document

logger = logging.getLogger(__name__)

class RechercherDocuments(_BaseConnexionBdd):
    
    def __init__(self):
        super().__init__()

    def recuperer_documents_semaine_courante(self) -> list[dict]: 
        """
        Récupère les documents dont la date (création/dépôt/publication/web) se situe dans les 7 derniers jours
        """
        fuseau_horaire = ZoneInfo("Europe/Paris")      
        date_du_jour = datetime.now(fuseau_horaire).date()
        six_jours_avant = date_du_jour - timedelta(days=6)

        with self.SessionLocal() as session:
            # ->       : extrait une valeur de type JSONB (par clé ou index)
            # ->>      : extrait une valeur de type text (par clé ou index)
            # ::[type] : notation de cast postgresql (ici en timestamptz)
            timestamps = [
                text("(payload -> 'cycleDeVie' -> 'chrono' ->> 'dateCreation')::timestamptz"),
                text("(payload -> 'cycleDeVie' -> 'chrono' ->> 'dateDepot')::timestamptz"),
                text("(payload -> 'cycleDeVie' -> 'chrono' ->> 'datePublication')::timestamptz"),
                text("(payload -> 'cycleDeVie' -> 'chrono' ->> 'datePublicationWeb')::timestamptz")
            ]

            conditions = []

            for timestamp in timestamps:
               conditions.append(
                    cast(timestamp, DATE).between(six_jours_avant, date_du_jour)
                )
            
            query = (
                select(Document.payload)
                    # coalesce : retourne la première condition non nulle, car une des date peut être absente
                    # *        : décompile la liste en arguments positionnels, ex (condition1, condition2, condition3,...)
                    .where(func.coalesce(*conditions))
                    .order_by(text("payload ->> 'uid'"))
            )

            documents_dict = session.execute(query).scalars().all()

        return documents_dict
    
    
    # --- Private Functions

    @staticmethod
    def _extraire_date_document(document_json: dict, fuseau_horaire: ZoneInfo) -> None | datetime.date:
        chrono = (
            document_json.get("cycleDeVie", {})
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
            date_time = RechercherDocuments._parse_isoaware(document_date)
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
    
    

