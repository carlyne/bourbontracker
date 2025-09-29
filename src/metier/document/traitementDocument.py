import logging
from typing import Sequence

from src.metier.applicationExceptions import DocumentIntrouvableException
from src.metier.document.document import Document
from src.metier.document.document import creer_document_depuis_fichier
from src.infra.stockageDocument import StockageDocument

class TraitementDocument:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
        self.stockage_document = StockageDocument()
    
    def recuperer_documents(self) -> list[Document] :
        self.stockage_document.mettre_a_jour()
        
        fichiers: Sequence[dict] = self.stockage_document.recuperer_documents_recents()

        if not fichiers:
            raise DocumentIntrouvableException("Aucun document trouvé")
        
        documents: list[Document] = [creer_document_depuis_fichier(fichier) for fichier in fichiers]

        self.stockage_document.vider_dossier_racice()

        return documents

