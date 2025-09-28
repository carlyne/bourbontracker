from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse, JSONResponse

from src.documentReponse import DocumentReponse
from src.metier.document.objet.documentLegislatif import Document
from src.metier.document.traitementDocument import TraitementDocument
from src.metier.applicationExceptions import DocumentIntrouvableException
from src.infra.infrastructureException import MiseAJourStockException, LectureException

traitement_document = TraitementDocument()

app = FastAPI(default_response_class=ORJSONResponse)

# --- Documents

@app.get(
    "/v1/documents/raw",
    response_model=list[Document],
    status_code=status.HTTP_200_OK,
)
def retournerDocumentsBrut( 
):
    return traitement_document.recuperer_documents()

@app.get(
    "/v1/documents-legislatifs",
    response_model=list[DocumentReponse],
    status_code=status.HTTP_200_OK,
)
def retournerDocumentLegislatif( 
):
    documentsLegislatifs = traitement_document._recuperer_documents_legislatifs()
    return [
        DocumentReponse.model_validate(documentLegislatif, from_attributes=True)
        for documentLegislatif in documentsLegislatifs
    ]

# --- Exceptions Handlers

def _json_error(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "status": status_code},
        media_type="application/json",
    )

@app.exception_handler(DocumentIntrouvableException)
def not_found_handler(_, exc: DocumentIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(MiseAJourStockException)
def download_handler(_, exc: MiseAJourStockException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(LectureException)
def read_handler(_, exc: LectureException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)