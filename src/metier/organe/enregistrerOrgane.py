import logging

from src.infra.organe.mettreAJourStockOrganes import MettreAJourStockOrganes

logger = logging.getLogger(__name__)

def créer_ou_raffraichir_données_organes():
    MettreAJourStockOrganes()
