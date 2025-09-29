from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse, JSONResponse

from src.metier.document.document import Document
from src.metier.acteur.acteur import Acteur
from src.metier.document.traitementDocument import TraitementDocument
from src.metier.acteur.traitementActeur import TraitementActeur
from src.metier.applicationExceptions import DocumentIntrouvableException, ActeurIntrouvableException
from src.infra.infrastructureException import MiseAJourStockException, LectureException

traitement_document = TraitementDocument()
traitement_acteur = TraitementActeur()

app = FastAPI(default_response_class=ORJSONResponse)

# --- Documents

@app.get(
    "/v1/documents",
    response_model=list[Document],
    status_code=status.HTTP_200_OK,
)
def retournerDocumentsBrut( 
):
    return traitement_document.recuperer_documents()

# --- Acteur

@app.get(
    "/v1/acteurs/{uid}",
    response_model=Acteur,
    status_code=status.HTTP_200_OK,
)
def retournerActeur(uid: str) -> Acteur:
    return traitement_acteur.recuperer_acteur(uid)

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

@app.exception_handler(ActeurIntrouvableException)
def not_found_handler(_, exc: DocumentIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(MiseAJourStockException)
def download_handler(_, exc: MiseAJourStockException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(LectureException)
def read_handler(_, exc: LectureException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)