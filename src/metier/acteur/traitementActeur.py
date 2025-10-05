import logging

from pydantic import ValidationError
from typing import Dict, List

from src.metier.organe.organe import Organe, parse_organe_depuis_payload
from src.infra.stockageActeur import StockageActeur
from src.metier.applicationExceptions import ActeurIntrouvableException
from src.metier.acteur.acteur import Acteur, Mandat, Mandats, parse_acteur_depuis_payload

logger = logging.getLogger(__name__)

class TraitementActeur:
    def __init__(self):
        self.stockage = StockageActeur()

    def recuperer_acteur(self, uid: str | None = None) -> Acteur:
        acteur_payload, organes_payload = self.stockage.recuperer_acteur_par_uid(uid)

        if not acteur_payload:
            raise ActeurIntrouvableException(f"Acteur introuvable pour uid='{uid}'")
        
        try:
            acteur: Acteur = parse_acteur_depuis_payload(acteur_payload)
            
            if not organes_payload:
                logger.warning("Aucun organe associé à l'acteur %s", uid)
                return acteur
                        
            organes: List[Organe] = [
                parse_organe_depuis_payload(organe_payload) for organe_payload in organes_payload or []
            ]

            organes_uids: Dict[str, Organe] = {
                organe.uid: organe for organe in organes if organe and organe.uid
            }
            
            mandats: List[Mandat] = acteur.mandats.mandat if (acteur.mandats and acteur.mandats.mandat) else []
            mandats_enrichis: List[Mandat] = []
                
            for mandat in mandats:
                organe_ref = mandat.organes.organeRef

                if mandat and mandat.organes and organe_ref:
                    detail = organes_uids.get(organe_ref)
                    organes_avec_detail = mandat.organes.model_copy(update={"detail": detail})
                    mandat = mandat.model_copy(update={"organes": organes_avec_detail})
                    
                mandats_enrichis.append(mandat)

            acteur = acteur.model_copy(update={"mandats": Mandats(mandat=mandats_enrichis)})
            
            return acteur
        
        except ValidationError as e: 
            logger.error("Erreur de validation pour le fichier Acteur avec uid=%s : %s", uid, e)
            raise ActeurIntrouvableException(
                f"Acteur invalide dans le fichier: {uid}.json"
            ) from e
        
    def enregistrer_acteurs(self):
        self.stockage.mettre_a_jour_et_enregistrer_acteurs()
