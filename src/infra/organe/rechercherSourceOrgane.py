from __future__ import annotations

import logging

from typing import Optional

from src.metier.organe.organe import Organe
from src.infra.infrastructureException import LectureException
from src.infra.baseConnexionBdd import BaseConnexionBdd
from src.infra.models import OrganeModel

logger = logging.getLogger(__name__)

class RechercherSourceOrgane(BaseConnexionBdd):
    def __init__(self) -> None :
        super().__init__()
        
    def recherche_par_uid(self, uid: str) -> Optional[Organe]:
        logger.debug("Recherche en base pour l'organe '%s'", uid)

        with self.ouvrir_session() as session:
            try:
                organe_model = session.get(OrganeModel, uid)

                if organe_model is None:
                    return None
                
                return Organe.model_validate(organe_model, from_attributes=True)
        
            except Exception as e:
                logger.error("Erreur lors de la lecture de l'Organe avec uid '%s'. Cause : %s", uid, e)
                raise LectureException(f"Erreur lors de la lecture de l'Organe avec uid '{uid}'")