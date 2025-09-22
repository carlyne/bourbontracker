import logging

from src.metier.documentIntrouvableException import DocumentIntrouvableException
from src.stockageDocument import StockageDocument
from src.reponseDocument import ReponseDocument

class TraitementDocument:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
        self.stockageDocument = StockageDocument()

    def recupererDocument(self):
        logging.info(f"Récupération du document")
        self.stockageDocument.mettreAJourStockDocuments()
        document= self.stockageDocument.recupererDocumentStocké()
        if document is None:
            logging.warning(f"Aucun document trouvé")
            raise DocumentIntrouvableException("Aucun document trouvé")
        return self.versReponseDocument(document)
    
    def versReponseDocument(self, document):
        return ReponseDocument(
            id=document.id,
            legislature=document.legislature,
            typeTexte=document.typeTexte,
            titrePrincipal=document.titrePrincipal,
            statutAdoption=document.statutAdoption,
            noticeFormule=document.noticeFormule,
            denominationStructurelle=document.denominationStructurelle,
            provenance=document.provenance,
            libelleClasse=document.libelleClasse,
            typeClassification=document.typeClassification,
            dateCreation=document.dateCreation,
            dateDepot=document.dateDepot,
            libelleDepot=document.libelleDepot,
            datePublication=document.datePublication,
            dossierId=document.dossierId,
            dossierUrl=document.dossierUrl
        )
    