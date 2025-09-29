import logging
from pydantic import ValidationError

from src.infra.stockageActeur import StockageActeur
from src.metier.applicationExceptions import ActeurIntrouvableException
from src.metier.acteur.acteur import Acteur, parse_acteur_depuis_fichier_json

logger = logging.getLogger(__name__)

class TraitementActeur:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"),
        self.stockage = StockageActeur()

    def recuperer_acteur(self, uid: str | None = None) -> Acteur:
        logging.debug("Récupération de l'acteur avec uid : %s)", uid)

        self.stockage.mettre_a_jour()
        fichier = self.stockage.recuperer_acteur_par_uid(uid)

        if fichier is None:
            raise ActeurIntrouvableException(f"Acteur introuvable pour uid='{uid}'")
        try:
            self.stockage.vider_dossier_racice()
            return parse_acteur_depuis_fichier_json(fichier)
        except ValidationError as e: 
            logger.error("Erreur de validation pour le fichier Acteur avec uid=%s : %s", uid, e)
            raise ActeurIntrouvableException(
                f"Acteur invalide dans le fichier: {uid}.json"
            ) from e
    
