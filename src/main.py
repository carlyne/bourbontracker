from fastapi import FastAPI, status, Query
from fastapi.responses import ORJSONResponse, JSONResponse

from src.documentLegislatifReponse import DocumentLegislatifReponse
from src.deputeEnExerciceReponse import DeputeEnExerciceReponse
from src.metier.documentLegislatif.objet.documentLegislatif import DocumentLegislatif
from src.metier.deputeEnExercice.objet.deputeEnExercice import DeputeEnExercice
from src.metier.documentLegislatif.traitementDocumentLegislatif import TraitementDocument
from src.metier.deputeEnExercice.traitementDeputeEnExercice import TraitementDeputeEnExercice
from src.metier.applicationExceptions import DocumentLegislatifIntrouvableException, DeputeEnExerciceIntrouvableException
from src.infra.infrastructureException import TelechargementException, LectureException

traitementDocument = TraitementDocument()
traitementActeur = TraitementDeputeEnExercice()

app = FastAPI(default_response_class=ORJSONResponse)

# --- Documents Legislatifs

@app.get(
    "/v1/documents-legislatifs",
    response_model=DocumentLegislatifReponse,
    status_code=status.HTTP_200_OK,
)
def retournerDocumentLegislatifBrut():
    document_legislatif = traitementDocument.recuperer_document()
    return DocumentLegislatifReponse.model_validate(document_legislatif)

@app.get(
    "/v1/documents-legislatifs/raw",
    response_model=DocumentLegislatif,
    status_code=status.HTTP_200_OK,
)
def retournerDocumentLegislatif():
    return traitementDocument.recuperer_document()

# --- Acteurs

@app.get(
    "/v1/deputes-en-exercice/raw",
    response_model=DeputeEnExercice,
    status_code=status.HTTP_200_OK
)
def retournerDeputeEnExerciceBrut(uid: str | None = Query(default=None, description="uid acteur (ex: PA722190)")):
    return traitementActeur.recuperer_acteur(uid)

@app.get(
    "/v1/deputes-en-exercice",
    response_model=DeputeEnExerciceReponse,
    status_code=status.HTTP_200_OK,
)
def retournerDeputeEnExercice(uid: str | None = Query(default=None, description="uid acteur (ex: PA722190)")):
    acteur = traitementActeur.recuperer_acteur(uid)
    uid_text = None
    if getattr(acteur, "acteur", None) and getattr(acteur.acteur, "uid", None):
        uid_text = acteur.acteur.uid.text

    return DeputeEnExerciceReponse(
        uid=uid_text,
        etatCivil=acteur.acteur.etatCivil if acteur.acteur else None,
        profession=acteur.acteur.profession if acteur.acteur else None,
    )

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

@app.exception_handler(DeputeEnExerciceIntrouvableException)
def acteur_not_found_handler(_, exc: DeputeEnExerciceIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(TelechargementException)
def download_handler(_, exc: TelechargementException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(LectureException)
def read_handler(_, exc: LectureException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)