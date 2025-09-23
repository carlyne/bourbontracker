from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse, JSONResponse

from src.documentLegislatifReponse import DocumentLegislatifReponse
from src.metier.documentLegislatif.objet.documentLegislatif import DocumentLegislatif
from src.metier.documentLegislatif.traitementDocument import TraitementDocument
from src.metier.documentLegislatif.documentIntrouvableException import DocumentIntrouvableException
from src.telechargementException import TelechargementException, LectureException

traitementDocument = TraitementDocument()

app = FastAPI(default_response_class=ORJSONResponse)

@app.get(
    "/v1/documents-legislatifs",
    response_model=DocumentLegislatifReponse,
    status_code=status.HTTP_200_OK,
)
def retournerDocument():
    document_legislatif = traitementDocument.recuperer_document()
    return DocumentLegislatifReponse.model_validate(document_legislatif)

@app.get(
    "/v1/documents-legislatifs/raw",
    response_model=DocumentLegislatif,
    status_code=status.HTTP_200_OK,
)
def retournerDocument():
    return traitementDocument.recuperer_document()

def _json_error(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "status": status_code},
        media_type="application/json",
    )

@app.exception_handler(DocumentIntrouvableException)
def not_found_handler(_, exc: DocumentIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(TelechargementException)
def download_handler(_, exc: TelechargementException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(LectureException)
def read_handler(_, exc: LectureException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)