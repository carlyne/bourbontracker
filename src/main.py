from fastapi import FastAPI, status, Query
from fastapi.responses import ORJSONResponse, JSONResponse
from typing import Annotated
from datetime import date

from src.documentLegislatifReponse import DocumentLegislatifReponse
from src.metier.documentLegislatif.objet.documentLegislatif import DocumentLegislatif
from src.metier.documentLegislatif.traitementDocumentLegislatif import TraitementDocumentLegislatif
from src.metier.applicationExceptions import DocumentLegislatifIntrouvableException
from src.infra.infrastructureException import MiseAJourStockException, LectureException
from src.infra.typeFiltrage import TypeFiltrage

traitement_document_legislatif = TraitementDocumentLegislatif()

app = FastAPI(default_response_class=ORJSONResponse)

# --- Documents Legislatifs

@app.get(
    "/v1/documents-legislatifs/raw",
    response_model=list[DocumentLegislatif],
    status_code=status.HTTP_200_OK,
)
def retournerDocumentLegislatifBrut( 
    date: Annotated[date | None, Query(description="ex: 2025-01-20")] = None,
    filtrage: Annotated[TypeFiltrage, Query(description='Type de filtrage: "jour", "semaine" (±3j dans le même mois), ou "mois"')] = TypeFiltrage.jour,
):
    return traitement_document_legislatif.recuperer_documents_legislatifs(date,filtrage)

@app.get(
    "/v1/documents-legislatifs",
    response_model=list[DocumentLegislatifReponse],
    status_code=status.HTTP_200_OK,
)
def retournerDocumentLegislatif( 
    date: Annotated[date | None, Query(description="ex: 2025-01-20")] = None,
    filtrage: Annotated[TypeFiltrage, Query(description='Type de filtrage: "jour", "semaine" (±3j dans le même mois), ou "mois"')] = TypeFiltrage.jour,
):
    documentsLegislatifs = traitement_document_legislatif.recuperer_documents_legislatifs(date,filtrage)
    return [
        DocumentLegislatifReponse.model_validate(documentLegislatif, from_attributes=True)
        for documentLegislatif in documentsLegislatifs
    ]

# --- Exceptions Handlers

def _json_error(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "status": status_code},
        media_type="application/json",
    )

@app.exception_handler(DocumentLegislatifIntrouvableException)
def not_found_handler(_, exc: DocumentLegislatifIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(MiseAJourStockException)
def download_handler(_, exc: MiseAJourStockException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(LectureException)
def read_handler(_, exc: LectureException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)