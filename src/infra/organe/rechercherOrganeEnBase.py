from __future__ import annotations

import logging

from typing import Optional

from src.infra.infrastructureException import LectureException
from src.infra.baseConnexionBdd import BaseConnexionBdd
from src.infra.models import OrganeModel

logger = logging.getLogger(__name__)

class RechercherOrganeEnBase(BaseConnexionBdd):
    def __init__(self) -> None :
        super().__init__()
        
    def recherche_par_uid(self, uid: str) -> Optional[OrganeModel]:
        with self.ouvrir_session() as session:
            try:
                return session.get(OrganeModel, uid)
            except Exception as e:
                logger.error("Erreur lors de la lecture de l'Organe avec uid '%s'. Cause : %s", uid, e)
                raise LectureException(f"Erreur lors de la lecture de l'Organe avec uid '{uid}'")