from http import HTTPStatus
from typing import Type, Mapping
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.metier.applicationExceptions import (
    ActeurIntrouvableException,
    DocumentIntrouvableException,
    OrganeIntrouvableException,
)
from src.infra.infrastructureException import (
    LectureException, 
    MiseAJourStockException
)

class GestionnaireException:
    """
    Cette classe permet de définir pour chaque type d’exception une réponse HTTP
    standardisée (code + format JSON), et de l’enregistrer dans une application (FastAPI).
    """
    def __init__(self):
        self._définition_des_types_de_réponses = {
            DocumentIntrouvableException: HTTPStatus.NOT_FOUND,
            ActeurIntrouvableException: HTTPStatus.NOT_FOUND,
            OrganeIntrouvableException: HTTPStatus.NOT_FOUND,
            MiseAJourStockException: HTTPStatus.INTERNAL_SERVER_ERROR,
            LectureException: HTTPStatus.INTERNAL_SERVER_ERROR,
            Exception: HTTPStatus.INTERNAL_SERVER_ERROR,
        }
       
    def _formater_réponse(
            self,
            message: str,
            code_réponse: HTTPStatus
    ) -> JSONResponse:
        """
        Crée une réponse JSON standardisée pour une erreur.
        """
        return JSONResponse(
            status_code=code_réponse,
            content={"detail": message, "status": code_réponse.value},
        )

    def _construire_réponse_pour_cette_exception(self, code_réponse: HTTPStatus):
        """
        Construit une fonction de gestion d’exception adaptée au code HTTP.
        La fonction retournée peut être passée à `app.add_exception_handler`.
        """
        async def constuire_réponse(requête: Request, exception: Exception) -> JSONResponse:
            return self._formater_réponse(str(exception), code_réponse)
        return constuire_réponse

    def configurer_réponses_par_types_d_exceptions(self, app: FastAPI) -> None:
        """
        Enregistre les handlers d’exception dans l’application pour que l'api renvoie la réponse souhaitée
        en cas d’exception interceptée.
        """
        for type_exception, code_réponse in self._définition_des_types_de_réponses.items():
            app.add_exception_handler(
                type_exception, 
                self._construire_réponse_pour_cette_exception(code_réponse)
            )