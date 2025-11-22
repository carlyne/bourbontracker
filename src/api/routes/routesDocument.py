from fastapi import APIRouter, Query, status

from src.api.schemas.documentReponse import DocumentReponse
from src.metier.document.document import Document
from src.metier.document.enregistrerDocuments import créer_ou_rafraichir_données_documents
from src.metier.document.recupererDocuments import (
    recuperer_documents_par_type_organe,
    recuperer_documents_semaine_courante,
)

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get(
    "",
    response_model=list[DocumentReponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Récupère les documents filtrés par type d'organe",
    responses={
        200: {"description": "Liste de documents retournée"},
        422: {"description": "Paramètre typeorgane manquant ou invalide"},
        500: {"description": "Erreur interne serveur"}
    }
)
def retourne_documents(typeorgane: str = Query(description="Type d'organe")) -> list[DocumentReponse]:
    documents: list[Document] = recuperer_documents_par_type_organe(typeorgane)

    return [
        DocumentReponse.model_validate(document.model_dump(mode="python", by_alias=True))
        for document in documents
    ]


@router.get(
    "/actualites",
    response_model=list[DocumentReponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Récupère les documents de la semaine courante",
    responses={
        200: {"description": "Liste de documents retournée"},
        500: {"description": "Erreur interne serveur"}
    }
)
def retourne_documents_semaines_courantes() -> list[DocumentReponse]:
    documents: list[Document] = recuperer_documents_semaine_courante()

    return [
        DocumentReponse.model_validate(document.model_dump(mode="python", by_alias=True))
        for document in documents
    ]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crée ou met à jour les données des documents",
    responses={
        201: {"description": "Traitement initié/réussi"},
        500: {"description": "Erreur interne serveur"}
    }
)
def crée_ou_raffraichis_données_documents():
    return créer_ou_rafraichir_données_documents()