import logging
from datetime import date
from typing import Sequence, List

from src.metier.applicationExceptions import DocumentLegislatifIntrouvableException
from src.infra.stockageDocumentLegislatif import StockageDocumentLegislatif
from src.infra.stockageActeur import StockageActeur
from src.metier.documentLegislatif.objet.documentLegislatif import DocumentLegislatif, parser as parse_doc
from src.infra.typeFiltrage import TypeFiltrage
from src.metier.acteur.objet.acteurDocument import ActeurDocument

class TraitementDocumentLegislatif:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
        self.stockage_document_legislatif = StockageDocumentLegislatif()
        self.stockage_acteur = StockageActeur()
    
    def recuperer_documents_legislatifs(
            self, 
            date: date | None,
            type_filtrage: TypeFiltrage = TypeFiltrage.jour
            ) -> list[DocumentLegislatif]:
        logging.info("Récupération des documents législatifs correspondants à la date %s", date)
        self.stockage_document_legislatif.mettre_a_jour_stock_documents_legislatifs()
        fichiers: Sequence[dict] = self.stockage_document_legislatif.recuperer_documents_legislatifs_par_date(date,type_filtrage)
        if not fichiers:
            raise DocumentLegislatifIntrouvableException("Aucun document législatif trouvé")
        
        docs: list[DocumentLegislatif] = [parse_doc(f) for f in fichiers]

        self.stockage_acteur.mettre_a_jour_stock_acteurs()

        docs_enrichis: list[DocumentLegislatif] = []
        for d in docs:
            refs: List[str] = []
            if d.auteurs and d.auteurs.auteur:
                for a in d.auteurs.auteur:
                    ar = getattr(getattr(a, "acteur", None), "acteur_ref", None)
                    if ar:
                        refs.append(ar)

            acteurs_docs: List[ActeurDocument] = []
            for ar in sorted(set(refs)):
                raw = self.stockage_acteur.lire_acteur_par_ref(ar)
                if not raw:
                    continue
                try:
                    acteurs_docs.append(ActeurDocument.from_acteur_json(raw))
                except Exception:
                    logging.exception("Mapping ActeurDocument impossible pour %s", ar)

            d2 = d.model_copy(update={"acteurs_documents": acteurs_docs})
            docs_enrichis.append(d2)
        
        self.stockage_document_legislatif.nettoyer_dossier_docs()

        return docs_enrichis

