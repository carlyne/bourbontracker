import logging
from pydantic import ValidationError

from src.metier.organe.organe import Organe, parse_organe_depuis_fichier_json
from src.infra.stockageOrgane import StockageOrgane
from src.metier.applicationExceptions import OrganeIntrouvableException

logger = logging.getLogger(__name__)

class TraitementOrgane:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"),
        self.stockage = StockageOrgane()

    def recuperer_organe(self, uid: str | None = None) -> Organe:
        logging.debug("Récupération de l'organe avec uid : %s)", uid)

        self.stockage.mettre_a_jour()
        fichier = self.stockage.recuperer_organe_par_uid(uid)

        if fichier is None:
            raise OrganeIntrouvableException(f"Organe introuvable pour uid='{uid}'")
        try:
            self.stockage.vider_dossier_racice()
            return parse_organe_depuis_fichier_json(fichier)
        except ValidationError as e: 
            logger.error("Erreur de validation pour le fichier Organe avec uid=%s : %s", uid, e)
            raise OrganeIntrouvableException(
                f"Organe invalide dans le fichier: {uid}.json"
            ) from e
    
