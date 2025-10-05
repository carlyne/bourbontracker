import logging

from src.infra.organe.mettreAJourStockOrganes import MettreAJourStockOrganes

logger = logging.getLogger(__name__)

def mettre_a_jour_organes():
    MettreAJourStockOrganes()
