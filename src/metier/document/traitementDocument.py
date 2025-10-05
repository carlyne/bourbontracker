from typing import Sequence

from src.metier.applicationExceptions import DocumentIntrouvableException
from src.metier.document.document import Document
from src.metier.document.document import creer_document_depuis_fichier
from src.infra.stockageDocument import StockageDocument

class TraitementDocument:
    def __init__(self):
        self.stockage_document = StockageDocument()
    
    def recuperer_documents(self) -> list[Document] :        
        fichiers: Sequence[dict] = self.stockage_document.recuperer_documents_semaine_courante()

        if not fichiers:
            raise DocumentIntrouvableException("Aucun document trouvé")
        
        documents: list[Document] = [creer_document_depuis_fichier(fichier) for fichier in fichiers]

        self.stockage_document.vider_dossier_racine()

        return documents
    
    def enregistrer_documents(self):
        self.stockage_document.mettre_a_jour_et_enregistrer_documents()

