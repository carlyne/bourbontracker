import logging
from pydantic import ValidationError

from src.metier.organe.organe import Organe
from src.infra.organe.rechercherOrgane import RechercherOrgane
from src.metier.applicationExceptions import OrganeIntrouvableException

logger = logging.getLogger(__name__)
    
def recuperer_organe(uid: str | None = None) -> Organe:
    rechercher_organe = RechercherOrgane()
    organe_en_base = rechercher_organe.recuperer_organe_par_uid(uid)

    if organe_en_base is None:
        raise OrganeIntrouvableException(f"Organe introuvable pour uid='{uid}'")

    try:
        return Organe.model_validate(organe_en_base)

    except ValidationError as e:
        logger.error("Erreur de validation pour l'organe avec uid=%s : %s", uid, e)
        raise OrganeIntrouvableException(
            f"Organe invalide en base pour uid='{uid}'"
        ) from e