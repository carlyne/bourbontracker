from collections.abc import Callable
from http import HTTPStatus
from typing import Type
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.metier.applicationExceptions import ActeurIntrouvableException, DocumentIntrouvableException, OrganeIntrouvableException
from src.infra.infrastructureException import LectureException, MiseAJourStockException

_ExceptionsReponse = Callable[[Request, Exception], JSONResponse]

def _format_erreur(message: str, code_reponse: HTTPStatus) -> JSONResponse:
    return JSONResponse(
        status_code=code_reponse,
        content={"detail": message, "status": code_reponse},
        media_type="application/json",
    )

def _construit_reponse(code_reponse: HTTPStatus) -> _ExceptionsReponse:
    def _exceptions_reponse(_: Request, exc: Exception) -> JSONResponse:
        return _format_erreur(str(exc), code_reponse)
    return _exceptions_reponse


_TYPE_EXCEPTIONS_ET_LEUR_CODES_REPONSES: dict[Type[Exception], HTTPStatus] = {
    DocumentIntrouvableException: HTTPStatus.NOT_FOUND,
    ActeurIntrouvableException: HTTPStatus.NOT_FOUND,
    OrganeIntrouvableException: HTTPStatus.NOT_FOUND,
    MiseAJourStockException: HTTPStatus.INTERNAL_SERVER_ERROR,
    LectureException: HTTPStatus.INTERNAL_SERVER_ERROR,
}

def enregistrer_réponses_par_type_d_exceptions(app: FastAPI) -> None:
    for type_exception, code_reponse in _TYPE_EXCEPTIONS_ET_LEUR_CODES_REPONSES.items():
        app.add_exception_handler(type_exception, _construit_reponse(code_reponse))

    app.add_exception_handler(Exception, _construit_reponse(HTTPStatus.INTERNAL_SERVER_ERROR))