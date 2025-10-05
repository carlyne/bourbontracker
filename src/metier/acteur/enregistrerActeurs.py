import logging

from src.infra.acteur.mettreAJourStockActeurs import MettreAJourStockActeurs

logger = logging.getLogger(__name__)
        
def mettre_a_jour_acteurs():
    MettreAJourStockActeurs()