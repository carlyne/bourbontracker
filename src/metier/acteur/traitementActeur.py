import logging
from pydantic import ValidationError

from src.infra.stockageActeur import StockageActeur
from src.metier.applicationExceptions import ActeurIntrouvableException
from src.metier.acteur.objet.acteur import Acteur, parse_acteur

logger = logging.getLogger(__name__)

class TraitementActeur:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.stockage = StockageActeur()

    def recuperer_acteur(self, uid: str | None = None) -> Acteur:
        logging.info("Récupération d'un acteur (uid=%s)", uid)
        self.stockage.mettre_a_jour_stock_acteurs()
        data, chemin = self.stockage.recuperer_acteur_depuis_uid(uid)
        if not data:
            raise ActeurIntrouvableException("Aucun acteur trouvé")
        try:
            return parse_acteur(data)
        except ValidationError as e: 
             logger.error(
                "Validation échouée pour le fichier: %s\nErreurs: %s",
                chemin, e.errors(),
                exc_info=True
            )
             raise ActeurIntrouvableException(
                f"Acteur invalide dans le fichier: {chemin}"
            ) from e
    
