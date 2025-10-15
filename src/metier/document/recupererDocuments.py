from typing import Dict, Iterable, List, Sequence, Set, Optional

from src.metier.acteur.recupererActeur import recuperer_acteur
from src.metier.applicationExceptions import DocumentIntrouvableException
from src.metier.acteur.recupererActeur import _convertir_acteur_v2_en_modele_metier
from src.metier.document.document import (
    Acteur as DocumentActeur,
    Auteur,
    Auteurs,
    Chrono,
    Classification,
    Classe,
    CycleDeVie,
    Depot,
    Document,
    Espece,
    Famille,
    Notice,
    OrganesReferents,
    SousType,
    Titres,
    Type_,
    parse_document_depuis_payload,
)
from src.infra.document.rechercherDocuments import RechercherDocuments
from src.infra.models import (
    ActeurV2 as ActeurV2Model,
    DocumentActeur as DocumentActeurModel,
    DocumentV2 as DocumentV2Model,
    OrganeV2 as OrganeV2Model,
)

def recuperer_documents_semaine_courante() -> list[Document]:
    documents = _recuperer_documents_semaine_courante()
    acteurs = _charger_acteurs(_collecter_acteurs_uids(documents))
    return _enrichir_documents(documents, acteurs)

def recuperer_documents_semaine_courante_v2() -> list[Document]:
    documents_v2 = _recuperer_documents_v2_semaine_courante()

    documents = [
        document
        for document in (_convertir_document_v2_en_modele_metier(document_v2) for document_v2 in documents_v2)
        if document and document.auteurs and document.auteurs.auteur
    ]

    if not documents:
        raise DocumentIntrouvableException("Aucun document trouvé")

    return documents

def _recuperer_documents_semaine_courante() -> Sequence[dict]:
    rechercher_documents = RechercherDocuments()
    payloads = rechercher_documents.recuperer_documents_semaine_courante()

    if not payloads:
        raise DocumentIntrouvableException("Aucun document trouvé")
    
    return [parse_document_depuis_payload(payload) for payload in payloads]  


def _recuperer_documents_v2_semaine_courante() -> list[DocumentV2Model]:
    rechercher_documents = RechercherDocuments()
    documents = rechercher_documents.recuperer_documents_semaine_courante()

    if not documents:
        raise DocumentIntrouvableException("Aucun document trouvé")

    return documents  

def _convertir_document_v2_en_modele_metier(document: DocumentV2Model) -> Optional[Document]:
    cycle_de_vie = _construire_cycle_de_vie(document)
    titres = _construire_titres(document)
    notice = _construire_notice(document)
    classification = _construire_classification(document)
    auteurs = _construire_auteurs(document)
    organes_referents = _construire_organes_referents(document)

    return Document(
        uid=document.uid,
        legislature=document.legislature,
        cycleDeVie=cycle_de_vie,
        denominationStructurelle=document.denomination_structurelle,
        provenance=document.provenance,
        titres=titres,
        divisions=None,
        dossierRef=document.dossier_ref,
        redacteur=document.redacteur,
        classification=classification,
        auteurs=Auteurs(auteur=auteurs) if auteurs else None,
        notice=notice,
        organesReferents=OrganesReferents(organeRef=organes_referents) if organes_referents else None,
    )

def _construire_cycle_de_vie(document: DocumentV2Model) -> Optional[CycleDeVie]:
    if not any(
        (
            document.date_creation,
            document.date_depot,
            document.date_publication,
            document.date_publication_web,
        )
    ):
        return None

    chrono = Chrono(
        dateCreation=document.date_creation,
        dateDepot=document.date_depot,
        datePublication=document.date_publication,
        datePublicationWeb=document.date_publication_web,
    )

    return CycleDeVie(chrono=chrono)


def _construire_titres(document: DocumentV2Model) -> Optional[Titres]:
    if not any((document.titre_principal, document.titre_principal_court)):
        return None
    return Titres(
        titrePrincipal=document.titre_principal,
        titrePrincipalCourt=document.titre_principal_court,
    )


def _construire_notice(document: DocumentV2Model) -> Optional[Notice]:
    if not any((document.notice_num_notice, document.notice_formule, document.notice_adoption_conforme)):
        return None
    return Notice(
        numNotice=document.notice_num_notice,
        formule=document.notice_formule,
        adoptionConforme=document.notice_adoption_conforme,
    )

def _construire_classification(document: DocumentV2Model) -> Optional[Classification]:
    famille = _construire_famille(document)
    type_ = _construire_type(document)
    sous_type = _construire_sous_type(document)

    if not any((famille, type_, sous_type, document.classification_statut_adoption)):
        return None

    return Classification(
        famille=famille,
        type_=type_,
        sousType=sous_type,
        statutAdoption=document.classification_statut_adoption,
    )


def _construire_famille(document: DocumentV2Model) -> Optional[Famille]:
    depot = Depot(
        code=document.classification_famille_depot_code,
        libelle=document.classification_famille_depot_libelle,
    )
    if not any((depot.code, depot.libelle)):
        depot = None

    classe = Classe(
        code=document.classification_famille_classe_code,
        libelle=document.classification_famille_classe_libelle,
    )
    if not any((classe.code, classe.libelle)):
        classe = None

    espece = Espece(
        code=document.classification_famille_espece_code,
        libelle=document.classification_famille_espece_libelle,
        libelleEdition=document.classification_famille_espece_libelle_edition,
    )
    if not any((espece.code, espece.libelle, espece.libelleEdition)):
        espece = None

    if depot is None and classe is None and espece is None:
        return None

    return Famille(depot=depot, classe=classe, espece=espece)


def _construire_type(document: DocumentV2Model) -> Optional[Type_]:
    if not any((document.classification_type_code, document.classification_type_libelle)):
        return None
    return Type_(
        code=document.classification_type_code,
        libelle=document.classification_type_libelle,
    )


def _construire_sous_type(document: DocumentV2Model) -> Optional[SousType]:
    if not any(
        (
            document.classification_sous_type_code,
            document.classification_sous_type_libelle,
            document.classification_sous_type_libelle_edition,
        )
    ):
        return None
    return SousType(
        code=document.classification_sous_type_code,
        libelle=document.classification_sous_type_libelle,
        libelleEdition=document.classification_sous_type_libelle_edition,
    )


def _construire_auteurs(document: DocumentV2Model) -> List[Auteur]:
    auteurs: List[Auteur] = []

    for auteur in document.auteurs:
        auteur_modele = _convertir_auteur(auteur)
        if auteur_modele is not None:
            auteurs.append(auteur_modele)

    return auteurs


def _convertir_auteur(auteur: DocumentActeurModel) -> Optional[Auteur]:
    acteur_detail = _convertir_acteur(auteur.acteur)

    if acteur_detail is None and not any((auteur.acteur_ref, auteur.qualite)):
        return None

    acteur = DocumentActeur(
        acteurRef=auteur.acteur_ref or auteur.acteur_uid,
        acteur_detail=acteur_detail,
        qualite=auteur.qualite,
    )

    return Auteur(acteur=acteur)


def _convertir_acteur(acteur: Optional[ActeurV2Model]):
    if acteur is None:
        return None

    organes = _collecter_organes_associes(acteur)
    return _convertir_acteur_v2_en_modele_metier(acteur, organes)


def _collecter_organes_associes(acteur: ActeurV2Model) -> List[OrganeV2Model]:
    organes_uniques: dict[str, OrganeV2Model] = {}

    for mandat in acteur.mandats:
        if mandat.organe is not None and mandat.organe.uid:
            organes_uniques[mandat.organe.uid] = mandat.organe

    return list(organes_uniques.values())


def _construire_organes_referents(document: DocumentV2Model) -> List[str]:
    return [ref for ref in document.organes_referents if ref]

def _collecter_acteurs_uids(documents: Iterable[Document]) -> Set[str]:
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

def _enrichir_documents(
        documents: Iterable[Document], 
        acteurs: Dict[str, object]
) -> list[Document]:
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

def _enrichir_auteurs(
        document: Document, 
        acteurs: Dict[str, object]
) -> List[Auteur]:
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
