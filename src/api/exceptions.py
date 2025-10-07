"""Exception handlers registration."""
from collections.abc import Callable
from http import HTTPStatus
from typing import Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.metier.applicationExceptions import (
    ActeurIntrouvableException,
    DocumentIntrouvableException,
    OrganeIntrouvableException,
)
from src.infra.infrastructureException import LectureException, MiseAJourStockException

_ExceptionHandler = Callable[[Request, Exception], JSONResponse]


def _json_error(message: str, status_code: HTTPStatus) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "status": status_code},
        media_type="application/json",
    )


def _build_handler(status_code: HTTPStatus) -> _ExceptionHandler:
    def _handler(_: Request, exc: Exception) -> JSONResponse:
        return _json_error(str(exc), status_code)

    return _handler


_EXCEPTION_STATUS_MAP: dict[Type[Exception], HTTPStatus] = {
    DocumentIntrouvableException: HTTPStatus.NOT_FOUND,
    ActeurIntrouvableException: HTTPStatus.NOT_FOUND,
    OrganeIntrouvableException: HTTPStatus.NOT_FOUND,
    MiseAJourStockException: HTTPStatus.INTERNAL_SERVER_ERROR,
    LectureException: HTTPStatus.INTERNAL_SERVER_ERROR,
}


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the given FastAPI application."""
    for exception_cls, status_code in _EXCEPTION_STATUS_MAP.items():
        app.add_exception_handler(exception_cls, _build_handler(status_code))

    app.add_exception_handler(Exception, _build_handler(HTTPStatus.INTERNAL_SERVER_ERROR))
