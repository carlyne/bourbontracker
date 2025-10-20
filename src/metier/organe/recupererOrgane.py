import logging
from typing import Optional

from src.infra.models import OrganeModel
from src.metier.organe.organe import Organe
from src.infra.organe.rechercherOrganeEnBase import RechercherOrganeEnBase
from src.metier.metierExceptions import (
    RecupererDonnéeException, 
    DonnéeIntrouvableException
)


logger = logging.getLogger(__name__)

    
def _parser_en_objet_metier(
        organe_model: OrganeModel, 
        uid: str
) -> Organe:
    try:
        return Organe.model_validate(organe_model)
    except Exception as e:
        logger.error("Erreur de validation pour l'organe avec uid '%s'. Cause : %s", uid, e)
        raise RecupererDonnéeException(f"Organe invalide pour uid '{uid}'") from e
    

def recuperer_organe(uid: str) -> Organe:
    rechercher_organe_en_base = RechercherOrganeEnBase()
    organe_model: Optional[OrganeModel] = rechercher_organe_en_base.recherche_par_uid(uid)

    if organe_model is None:
        raise DonnéeIntrouvableException(f"Aucun Organe trouvé pour l'uid '{uid}'")
    
    return _parser_en_objet_metier(organe_model, uid)