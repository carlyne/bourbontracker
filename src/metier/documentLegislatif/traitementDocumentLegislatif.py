import logging
from datetime import date
from typing import Sequence

from src.metier.applicationExceptions import DocumentLegislatifIntrouvableException
from src.infra.stockageDocument import StockageDocumentLegislatif
from src.metier.documentLegislatif.objet import documentLegislatif
from src.metier.documentLegislatif.objet.documentLegislatif import DocumentLegislatif
from src.infra.typeFiltrage import TypeFiltrage

class TraitementDocumentLegislatif:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
        self.stockage = StockageDocumentLegislatif()
    
    def recuperer_documents_legislatifs(
            self, 
            date: date | None,
            type_filtrage: TypeFiltrage = TypeFiltrage.jour
            ) -> list[DocumentLegislatif]:
        logging.info("Récupération des documents législatifs correspondants à la date %s", date)
        self.stockage.mettre_a_jour_stock_documents_legislatifs()
        fichiers: Sequence[dict] = self.stockage.recuperer_documents_legislatifs_par_date(date,type_filtrage)
        if not fichiers:
            raise DocumentLegislatifIntrouvableException("Aucun document législatif trouvé")
        return [documentLegislatif.parser(fichier) for fichier in fichiers]
