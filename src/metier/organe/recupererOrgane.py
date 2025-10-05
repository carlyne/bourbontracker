import logging
from pydantic import ValidationError

from src.metier.organe.organe import Organe, parse_organe_depuis_payload
from src.infra.organe.rechercherOrgane import RechercherOrgane
from src.metier.applicationExceptions import OrganeIntrouvableException

logger = logging.getLogger(__name__)
        
def recuperer_organe(uid: str | None = None) -> Organe:
    rechercher_organe = RechercherOrgane()
    organe_payload = rechercher_organe.recuperer_organe_par_uid(uid)

    if not organe_payload:
        raise OrganeIntrouvableException(f"Organe introuvable pour uid='{uid}'")
    
    try:
        return parse_organe_depuis_payload(organe_payload)
    
    except ValidationError as e: 
        logger.error("Erreur de validation pour le fichier Organe avec uid=%s : %s", uid, e)
        raise OrganeIntrouvableException(
            f"Organe invalide dans le fichier: {uid}.json"
        ) from e