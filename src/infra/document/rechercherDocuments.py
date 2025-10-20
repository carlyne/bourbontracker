from __future__ import annotations

import logging

from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.infra.baseConnexionBdd import BaseConnexionBdd
from src.infra.models import DocumentModel, ActeurModel, DocumentActeurModel, MandatModel

logger = logging.getLogger(__name__)

class RechercherDocuments(BaseConnexionBdd):
    
    def __init__(self):
        super().__init__()
    

    def recuperer_documents_semaine_courante(self) -> list[DocumentModel]:
        """Retourne les documents récents accompagnés de leurs auteurs et mandats."""
        fuseau_horaire = ZoneInfo("Europe/Paris")
        date_du_jour = datetime.now(fuseau_horaire).date()
        six_jours_avant = date_du_jour - timedelta(days=6)

        with self.ouvrir_session() as session:
            conditions = [
                func.date(DocumentModel.date_creation).between(six_jours_avant, date_du_jour),
                func.date(DocumentModel.date_depot).between(six_jours_avant, date_du_jour),
                func.date(DocumentModel.date_publication).between(six_jours_avant, date_du_jour),
                func.date(DocumentModel.date_publication_web).between(six_jours_avant, date_du_jour),
            ]

            query = (
                select(DocumentModel)
                .options(
                    selectinload(DocumentModel.auteurs)
                    .joinedload(DocumentActeurModel.acteur)
                    .selectinload(ActeurModel.mandats)
                    .options(
                        joinedload(MandatModel.organe),
                        selectinload(MandatModel.collaborateurs),
                        selectinload(MandatModel.suppleants),
                    )
                )
                .where(or_(*conditions))
                .order_by(DocumentModel.uid)
            )

            documents = session.execute(query).scalars().unique().all()

        if not documents:
            logger.info("Aucun document trouvé dans la période récente")

        return documents
    
    
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
    
    

