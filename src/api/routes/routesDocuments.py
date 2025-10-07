from fastapi import APIRouter, status

from src.api.routes.documentReponse import DocumentReponse
from src.metier.document.document import Document
from src.metier.document.enregistrerDocuments import mettre_a_jour_documents
from src.metier.document.recupererDocuments import recuperer_documents_semaine_courante

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get(
    "",
    response_model=list[DocumentReponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def retourne_documents() -> list[DocumentReponse]:
    documents: list[Document] = recuperer_documents_semaine_courante()
    return [
        DocumentReponse.model_validate(document.model_dump(mode="python", by_alias=True))
        for document in documents
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def met_a_jour_documents():
    return mettre_a_jour_documents()