import logging

from src.metier.documentLegislatif.documentIntrouvableException import DocumentIntrouvableException
from src.stockageDocument import StockageDocument
from src.metier.documentLegislatif.objet import documentLegislatif

class TraitementDocument:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
        self.stockage_document = StockageDocument()

    def recuperer_document(self):
        logging.info(f"Récupération du document legislatif ")
        self.stockage_document.mettre_a_jour_stock_documents()
        fichier= self.stockage_document.recuperer_document_stocké()
        if fichier is None:
            logging.warning(f"Aucun document legislatif trouvé")
            raise DocumentIntrouvableException("Aucun document legislatif trouvé")
        return documentLegislatif.parser(fichier)