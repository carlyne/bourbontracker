import logging
from datetime import date, datetime
from typing import Sequence, List

from src.metier.applicationExceptions import DocumentIntrouvableException
from src.metier.document.objetv2.document import creer_document_depuis_fichier
from src.infra.stockageDocument import StockageDocument
from src.infra.stockageActeur import StockageActeur
from src.metier.document.objet.documentLegislatif import Document, parser as parse_doc
from src.metier.acteur.objet.acteurDocument import ActeurDocument

class TraitementDocument:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
        self.stockage_document = StockageDocument()
        self.stockage_acteur = StockageActeur()
    
   
    def recuperer_documents(self) -> list[Document] :
        self.stockage_document.mettre_a_jour()
        
        fichiers: Sequence[dict] = self.stockage_document.recuperer_documents_recents()

        if not fichiers:
            raise DocumentIntrouvableException("Aucun document trouvé")
        
        documents: list[Document] = [creer_document_depuis_fichier(fichier) for fichier in fichiers]

        self.stockage_document.vider_dossier_racice()

        return documents
        
   
    def _recuperer_documents_legislatifs(
            self
            ) -> list[Document]:
        
        logging.debug("Récupération des documents législatifs correspondants à la date %s", date)

        self.stockage_document.mettre_a_jour()
        
        fichiers: Sequence[dict] = self.stockage_document.recuperer_documents_recents()
        if not fichiers:
            raise DocumentIntrouvableException("Aucun document législatif trouvé")
        
        docs: list[Document] = [parse_doc(f) for f in fichiers]

        self.stockage_acteur.mettre_a_jour()

        docs_enrichis: list[Document] = []
        for d in docs:
            refs: List[str] = []
            if d.auteurs and d.auteurs.auteur:
                for a in d.auteurs.auteur:
                    ar = getattr(getattr(a, "acteur", None), "acteur_ref", None)
                    if ar:
                        refs.append(ar)

            acteurs_docs: List[ActeurDocument] = []
            for ar in sorted(set(refs)):
                raw = self.stockage_acteur.recuperer_acteur_par_ref(ar)
                if not raw:
                    continue
                try:
                    acteurs_docs.append(ActeurDocument.from_acteur_json(raw))
                except Exception:
                    logging.exception("Mapping ActeurDocument impossible pour %s", ar)

            d2 = d.model_copy(update={"acteurs_documents": acteurs_docs})
            docs_enrichis.append(d2)

        docs_enrichis.sort(key=self._sort_key, reverse=True)
        
        self.stockage_document.vider_dossier_racice()

        return docs_enrichis

    def _sort_key(self, document_legislatif: Document):
            date_creation = self._date_creation(document_legislatif)
            return (date_creation is not None, date_creation or datetime.min)
    
    def _date_creation(self, document_legislatif: Document) -> datetime | None:
        return getattr(getattr(getattr(document_legislatif, "cycle_de_vie", None), "chrono", None), "date_creation", None)


