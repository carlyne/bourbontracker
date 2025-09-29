import logging
from pydantic import ValidationError
from typing import List

from src.metier.organe.organe import Organe
from src.metier.organe.traitementOrgane import TraitementOrgane
from src.infra.stockageActeur import StockageActeur
from src.metier.applicationExceptions import ActeurIntrouvableException
from src.metier.acteur.acteur import Acteur, parse_acteur_depuis_fichier_json

logger = logging.getLogger(__name__)

class TraitementActeur:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"),
        self.stockage_acteur = StockageActeur()
        self.traitement_organe = TraitementOrgane()

    def recuperer_acteur(self, uid: str | None = None) -> Acteur:
        logging.debug("Récupération de l'acteur avec uid : %s)", uid)

        self.stockage_acteur.mettre_a_jour()
        fichier = self.stockage_acteur.recuperer_acteur_par_uid(uid)

        if fichier is None:
            raise ActeurIntrouvableException(f"Acteur introuvable pour uid='{uid}'")
        try:
            
            acteur: Acteur = parse_acteur_depuis_fichier_json(fichier)
            organes_ref: List[str] = self._extraire_organe_refs(acteur)
            
            if not organes_ref:
                logger.warning("Aucun organeRef trouvé pour l'acteur %s", uid)
                return acteur
            
            organes: List[Organe] = []

            for organe_ref in organes_ref:
                try:
                    organe: Organe = self.traitement_organe.recuperer_organe(organe_ref)
                    organes.append(organe)
                except Exception as e:
                    logger.error("un des Organe ne peut pas être récupéré pour l'acteur %s : %s", uid, e)
                    raise ActeurIntrouvableException(
                        f"Acteur avec Organe invalide dans le fichier: {uid}.json"
                    ) from e
                
            acteur = acteur.model_copy(update={"organes_acteur": organes})

            self.stockage_acteur.vider_dossier_racice()
            
            return acteur
        except ValidationError as e: 
            logger.error("Erreur de validation pour le fichier Acteur avec uid=%s : %s", uid, e)
            raise ActeurIntrouvableException(
                f"Acteur invalide dans le fichier: {uid}.json"
            ) from e

    
    # --- Private Functions

    @staticmethod
    def _extraire_organe_refs(acteur: Acteur) -> List[str]:
        mandats = acteur.mandats.mandat if (acteur.mandats and acteur.mandats.mandat) else []
        refs = [
            mandat.organes.organeRef
            for mandat in mandats
            if mandat and mandat.organes and mandat.organes.organeRef
        ]
        return list(dict.fromkeys(refs))