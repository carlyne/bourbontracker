import logging

from typing import Optional

from src.infra.infrastructureException import LectureException
from src.metier.acteur.acteur import Acteur
from src.infra.acteur.rechercherSourceActeur import RechercherSourceActeur
from src.metier.metierExceptions import DonnéeIntrouvableException, RecupererDonnéeException


logger = logging.getLogger(__name__)


def recuperer_acteur(
    uid: str,
    legislature: Optional[str] = None,
    type_organe: Optional[str] = None

) -> Acteur:
    
    rechercher_source_acteur = RechercherSourceActeur()

    try:
        logger.debug(
            "Récupération de l'acteur '%s' pour la législature '%s' et le type d'organe '%s'", 
            uid,legislature,type_organe
        )

        acteur = rechercher_source_acteur.recherche_par_uid_et_critères(
            uid, 
            legislature, 
            type_organe
        )

    except LectureException as e:
        raise RecupererDonnéeException(f"L'acteur '{uid}' n'a pas pu être récupéré en base") from e

    if acteur is None:
        logger.warning("L'acteur '%s' n'existe pas", uid)
        raise DonnéeIntrouvableException(f"L'acteur '{uid}' n'existe pas")
    
    return acteur