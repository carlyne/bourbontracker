from typing import Dict, Iterable, List, Sequence, Set

from src.metier.acteur.recupererActeur import recuperer_acteur
from src.metier.applicationExceptions import DocumentIntrouvableException
from src.metier.document.document import Auteur, Auteurs, Document
from src.metier.document.document import parse_document_depuis_payload
from src.infra.document.rechercherDocuments import RechercherDocuments

def recuperer_documents_semaine_courante() -> list[Document]:
    payloads = _recuperer_payloads_semaine_courante()
    documents = _parser_documents(payloads)
    acteurs = _charger_acteurs(_collecter_acteur_uids(documents))
    return _enrichir_documents(documents, acteurs)


def _recuperer_payloads_semaine_courante() -> Sequence[dict]:
    rechercher_documents = RechercherDocuments()
    payloads = rechercher_documents.recuperer_documents_semaine_courante()
    if not payloads:
        raise DocumentIntrouvableException("Aucun document trouvé")
    return payloads


def _parser_documents(payloads: Sequence[dict]) -> list[Document]:
    return [parse_document_depuis_payload(payload) for payload in payloads]


def _collecter_acteur_uids(documents: Iterable[Document]) -> Set[str]:
    acteur_uids: Set[str] = set()
    for document in documents:
        for auteur in _extraire_auteurs(document):
            acteur_ref = getattr(getattr(auteur, "acteur", None), "acteurRef", None)
            if acteur_ref:
                acteur_uids.add(acteur_ref)
    return acteur_uids


def _extraire_auteurs(document: Document) -> List[Auteur]:
    if document.auteurs and document.auteurs.auteur:
        return list(document.auteurs.auteur)
    return []


def _charger_acteurs(acteur_uids: Iterable[str]) -> Dict[str, object]:
    cache: Dict[str, object] = {}
    for acteur_uid in acteur_uids:
        try:
            cache[acteur_uid] = recuperer_acteur(acteur_uid)
        except Exception:
            continue
    return cache


def _enrichir_documents(documents: Iterable[Document], acteurs: Dict[str, object]) -> list[Document]:
    documents_enrichis: list[Document] = []
    for document in documents:
        auteurs_enrichis = _enrichir_auteurs(document, acteurs)
        if not auteurs_enrichis:
            continue
        auteurs_wrapped = (
            document.auteurs.model_copy(update={"auteur": auteurs_enrichis})
            if document.auteurs
            else Auteurs(auteur=auteurs_enrichis)
        )
        documents_enrichis.append(
            document.model_copy(update={"auteurs": auteurs_wrapped})
        )
    return documents_enrichis


def _enrichir_auteurs(document: Document, acteurs: Dict[str, object]) -> List[Auteur]:
    auteurs_enrichis: List[Auteur] = []
    for auteur in _extraire_auteurs(document):
        acteur_ref = getattr(getattr(auteur, "acteur", None), "acteurRef", None)
        if not acteur_ref:
            auteurs_enrichis.append(auteur)
            continue

        detail = acteurs.get(acteur_ref)
        if not detail:
            continue

        acteur_mod = auteur.acteur.model_copy(update={"acteur_detail": detail})
        auteurs_enrichis.append(
            auteur.model_copy(update={"acteur": acteur_mod})
        )
    return auteurs_enrichis

