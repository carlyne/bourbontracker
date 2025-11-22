from __future__ import annotations

import logging
from typing import List

from src.metier.document.document import Document
from src.infra.infrastructureException import LectureException
from src.metier.metierExceptions import DonnéeIntrouvableException, RecupererDonnéeException
from src.infra.document.rechercherSourceDocuments import RechercherSourceDocuments

logger = logging.getLogger(__name__)

def recuperer_documents_semaine_courante() -> List[Document]:
    rechercher_source_documents = RechercherSourceDocuments()

    try:
        logger.debug("Récupération des documents de la semaine courante")

        documents = rechercher_source_documents.recherche_sur_semaine_courante()

    except LectureException as e:
        raise RecupererDonnéeException("Les documents de la semaine courante n'ont pas pu être récupérés") from e
    
    if not documents:
        logger.warning("Pas de document sur la semaine courante")
        raise DonnéeIntrouvableException(f"Pas de document sur la semaine courante")

    return documents


def recuperer_documents_par_type_organe(type_organe: str) -> List[Document]:
    rechercher_source_documents = RechercherSourceDocuments()

    try:
        logger.debug("Récupération des documents pour le type d'organe : %s", type_organe)
        return rechercher_source_documents.recherche_par_type_organe(type_organe)

    except LectureException as e:
        raise RecupererDonnéeException(
            "Les documents pour ce type d'organe n'ont pas pu être récupérés"
        ) from e
