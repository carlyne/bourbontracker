import logging
from pydantic import ValidationError

from src.infra.stockageDeputeEnExercice import StockageDeputeEnExercice
from src.metier.applicationExceptions import DeputeEnExerciceIntrouvableException
from src.metier.deputeEnExercice.objet.deputeEnExercice import DeputeEnExercice, parse_depute

logger = logging.getLogger(__name__)

class TraitementDeputeEnExercice:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.stockage = StockageDeputeEnExercice()

    def recuperer_acteur(self, uid: str | None = None) -> DeputeEnExercice:
        logging.info("Récupération d'un acteur (uid=%s)", uid)
        self.stockage.mettre_a_jour_stock_acteurs()
        data, chemin = self.stockage.lire_acteur_par_uid(uid)
        if not data:
            raise DeputeEnExerciceIntrouvableException("Aucun acteur trouvé")
        try:
            return parse_depute(data)
        except ValidationError as e: 
             logger.error(
                "Validation Pydantic échouée pour le fichier: %s\nErreurs: %s",
                chemin, e.errors(),
                exc_info=True
            )
             raise DeputeEnExerciceIntrouvableException(
                f"Acteur invalide dans le fichier: {chemin}"
            ) from e
    
