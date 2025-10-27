import logging

from src.infra.infrastructureException import LectureException
from src.metier.organe.organe import Organe
from src.infra.organe.rechercherSourceOrgane import RechercherSourceOrgane
from src.metier.metierExceptions import RecupererDonnéeException, DonnéeIntrouvableException


logger = logging.getLogger(__name__)


def recuperer_organe(uid: str) -> Organe:
    rechercher_source_organe = RechercherSourceOrgane()

    try:
        logger.debug("Récupération de l'organe '%s'", uid)

        organe = rechercher_source_organe.recherche_par_uid(uid)

    except LectureException as e:
        raise RecupererDonnéeException(f"L'organe '{uid}' n'a pas pu être récupéré en base") from e

    if organe is None:
        logger.warning("L'organe '%s' n'existe pas", uid)
        raise DonnéeIntrouvableException(f"L'organe '{uid}' n'existe pas")
    
    return organe