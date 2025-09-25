from fastapi import FastAPI, status, Query
from fastapi.responses import ORJSONResponse, JSONResponse
from typing import Annotated
from datetime import date

from src.documentLegislatifReponse import DocumentLegislatifReponse
""" from src.acteurReponse import ActeurReponse
from src.metier.acteur.objet.acteur import Acteur """
from src.metier.documentLegislatif.traitementDocumentLegislatif import TraitementDocumentLegislatif
#from src.metier.acteur.traitementActeur import TraitementActeur
from src.metier.applicationExceptions import DocumentLegislatifIntrouvableException, ActeurIntrouvableException
from src.infra.infrastructureException import TelechargementException, LectureException
from src.infra.typeFiltrage import TypeFiltrage

traitementDocument = TraitementDocumentLegislatif()
#traitementActeur = TraitementActeur()

app = FastAPI(default_response_class=ORJSONResponse)

# --- Documents Legislatifs

@app.get(
    "/v1/documents-legislatifs",
    response_model=list[DocumentLegislatifReponse],
    status_code=status.HTTP_200_OK,
)
def retournerDocumentLegislatifBrut( 
    date: Annotated[date | None, Query(description="ex: 2025-01-20")] = None,
    filtrage: Annotated[TypeFiltrage, Query(description='Type de filtrage: "jour", "semaine" (±3j dans le même mois), ou "mois"')] = TypeFiltrage.jour,
):
    documentsLegislatifs = traitementDocument.recuperer_documents_legislatifs(date,filtrage)
    return [
        DocumentLegislatifReponse.model_validate(documentLegislatif, from_attributes=True)
        for documentLegislatif in documentsLegislatifs
    ]

# --- Acteurs

""" @app.get(
    "/v1/acteurs/raw",
    response_model=Acteur,
    status_code=status.HTTP_200_OK
)
def retournerActeurBrut(uid: str | None = Query(default=None, description="uid acteur (ex: PA722190)")):
    return traitementActeur.recuperer_acteur(uid)

@app.get(
    "/v1/acteurs",
    response_model=ActeurReponse,
    status_code=status.HTTP_200_OK,
)
def retournerDeputeEnExercice(uid: str | None = Query(default=None, description="uid acteur (ex: PA722190)")):
    acteur = traitementActeur.recuperer_acteur(uid)
    uid_text = acteur.uid.text if (acteur and acteur.uid and acteur.uid.text) else None

    return ActeurReponse(
        uid=uid_text,
        etatCivil=acteur.etatCivil,
        profession=acteur.profession,
    ) """

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

""" @app.exception_handler(ActeurIntrouvableException)
def acteur_not_found_handler(_, exc: ActeurIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)
 """
@app.exception_handler(TelechargementException)
def download_handler(_, exc: TelechargementException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(LectureException)
def read_handler(_, exc: LectureException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)