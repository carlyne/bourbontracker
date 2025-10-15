from __future__ import annotations

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.models import ActeurV2, DocumentActeur, DocumentV2, Mandat

logger = logging.getLogger(__name__)


class RechercherDocuments(_BaseConnexionBdd):

    def __init__(self):
        super().__init__()

    def recuperer_documents_semaine_courante(self) -> list[DocumentV2]:
        """Retourne les documents récents accompagnés de leurs auteurs et mandats."""
        fuseau_horaire = ZoneInfo("Europe/Paris")
        date_du_jour = datetime.now(fuseau_horaire).date()
        six_jours_avant = date_du_jour - timedelta(days=6)

        with self.SessionLocal() as session:
            conditions = [
                func.date(DocumentV2.date_creation).between(six_jours_avant, date_du_jour),
                func.date(DocumentV2.date_depot).between(six_jours_avant, date_du_jour),
                func.date(DocumentV2.date_publication).between(six_jours_avant, date_du_jour),
                func.date(DocumentV2.date_publication_web).between(six_jours_avant, date_du_jour),
            ]

            query = (
                select(DocumentV2)
                .options(
                    selectinload(DocumentV2.auteurs)
                    .joinedload(DocumentActeur.acteur)
                    .selectinload(ActeurV2.mandats)
                    .joinedload(Mandat.organe)
                )
                .where(or_(*conditions))
                .order_by(DocumentV2.uid)
            )

            documents = session.execute(query).scalars().unique().all()

        if not documents:
            logger.info("Aucun document trouvé dans la période récente")

        return documents
