from typing import Dict, List, Sequence, Set

from src.metier.acteur.recupererActeur import recuperer_acteur
from src.metier.applicationExceptions import DocumentIntrouvableException
from src.metier.document.document import Auteur, Auteurs, Document
from src.metier.document.document import parse_document_depuis_payload
from src.infra.document.rechercherDocuments import RechercherDocuments

def recuperer_documents_semaine_courante() -> list[Document] :  
        rechercher_documents = RechercherDocuments()      
        payloads: Sequence[dict] = rechercher_documents.recuperer_documents_semaine_courante()
        if not payloads:
            raise DocumentIntrouvableException("Aucun document trouvé")
        return [parse_document_depuis_payload(payload) for payload in payloads]

def recuperer_documents_semaine_courante_avec_acteurs() -> list[Document]:
    rechercher_documents = RechercherDocuments()
    payloads: Sequence[dict] = rechercher_documents.recuperer_documents_semaine_courante()
    if not payloads:
        raise DocumentIntrouvableException("Aucun document trouvé")

    documents: list[Document] = [parse_document_depuis_payload(payload) for payload in payloads]

    acteurs_uids: Set[str] = set()
    for document in documents:
        auteurs = (document.auteurs.auteur if (document.auteurs and document.auteurs.auteur) else [])

        for auteur in auteurs:
            if auteur and auteur.acteur and auteur.acteur.acteurRef:
                acteurs_uids.add(auteur.acteur.acteurRef)

    cache_acteurs: Dict[str, object] = {}
    for acteur_uid in acteurs_uids:
        try:
            cache_acteurs[acteur_uid] = recuperer_acteur(acteur_uid)
        except Exception:
            continue

    documents_enrichis: list[Document] = []

    for document in documents:
        auteurs = (document.auteurs.auteur if (document.auteurs and document.auteurs.auteur) else [])
        
        auteurs_enrichis: List[Auteur] = []

        for auteur in auteurs:
            if auteur and auteur.acteur and auteur.acteur.acteurRef:
                detail = cache_acteurs.get(auteur.acteur.acteurRef)
                acteur_mod = auteur.acteur.model_copy(update={"acteur_detail": detail})
                auteur = auteur.model_copy(update={"acteur": acteur_mod})
            auteurs_enrichis.append(auteur)

        auteurs_wrapped = document.auteurs.model_copy(update={"auteur": auteurs_enrichis}) if document.auteurs else Auteurs(auteur=auteurs_enrichis)
        document_enrichi = document.model_copy(update={"auteurs": auteurs_wrapped})
        documents_enrichis.append(document_enrichi)

    return documents_enrichis

