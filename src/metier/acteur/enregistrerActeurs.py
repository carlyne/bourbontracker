import logging

from src.infra.acteur.mettreAJourStockActeurs import MettreAJourStockActeurs

logger = logging.getLogger(__name__)
        
def créer_ou_raffraichir_données_acteurs():
    MettreAJourStockActeurs()