from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.metier.organe.recupererOrgane import recuperer_organe
from src.metier.acteur.recupererActeur import recuperer_acteur
from src.organeReponse import OrganeReponse
from src.acteurReponse import ActeurReponse
from src.documentReponse import DocumentReponse
from src.metier.organe.organe import Organe
from src.metier.organe.enregistrerOrgane import mettre_a_jour_organes
from src.metier.document.document import Document
from src.metier.acteur.acteur import Acteur
from src.metier.document.recupererDocuments import recuperer_documents_semaine_courante
from src.metier.document.enregistrerDocuments import mettre_a_jour_documents
from src.metier.acteur.enregistrerActeurs import mettre_a_jour_acteurs
from src.metier.applicationExceptions import DocumentIntrouvableException, ActeurIntrouvableException, OrganeIntrouvableException
from src.infra.infrastructureException import MiseAJourStockException, LectureException

app = FastAPI(default_response_class=ORJSONResponse)

origins = [
    "http://localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Documents

@app.get(
    "/v1/documents",
    response_model=list[DocumentReponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def retourner_documents():
    documents: list[Document] = recuperer_documents_semaine_courante()
    return [
        DocumentReponse.model_validate(document.model_dump(mode="python", by_alias=True))
        for document in documents
    ]

@app.post(
    "/v1/documents",
    status_code=status.HTTP_201_CREATED,
)
def enregistrer_documents():
    return mettre_a_jour_documents()


# --- Acteur

@app.get(
    "/v1/acteurs/{uid}",
    response_model=ActeurReponse, 
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def retourner_acteur(uid: str):
    acteur: Acteur = recuperer_acteur(uid)
    return ActeurReponse.model_validate(
        acteur.model_dump(mode="python", by_alias=True)
    )

@app.post(
    "/v1/acteurs",
    status_code=status.HTTP_201_CREATED,
)
def enregistrer_acteurs():
    return mettre_a_jour_acteurs()


# --- Organe

@app.get(
    "/v1/organes/{uid}",
    response_model=OrganeReponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def retourner_organe(uid: str):
    organe: Organe = recuperer_organe(uid)
    return OrganeReponse.model_validate(
        organe.model_dump(mode="python", by_alias=True)
    )

@app.post(
    "/v1/organes",
    status_code=status.HTTP_201_CREATED,
)
def enregistrer_organes():
    return mettre_a_jour_organes()


# --- Exceptions Handlers

def _json_error(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "status": status_code},
        media_type="application/json",
    )

@app.exception_handler(DocumentIntrouvableException)
def document_not_found_handler(_, exc: DocumentIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(ActeurIntrouvableException)
def acteur_not_found_handler(_, exc: ActeurIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(OrganeIntrouvableException)
def organe_not_found_handler(_, exc: OrganeIntrouvableException):
    return _json_error(str(exc), status.HTTP_404_NOT_FOUND)

@app.exception_handler(MiseAJourStockException)
def download_handler(_, exc: MiseAJourStockException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(LectureException)
def read_handler(_, exc: LectureException):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(Exception)
def general_handler(_, exc: Exception):
    return _json_error(str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)