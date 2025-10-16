from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, RedirectResponse

from src.api.gestionnaireExceptions import GestionnaireException
from src.api.routes import routesActeurs, routesDocuments, routesOrganes
from src.settings import settings

_gestionnaire_exceptions = GestionnaireException()

def _configurer_cors(
        app: FastAPI, 
        cors_origin_autorisées: Sequence[str]
) -> None:
    """
    Ajoute le middleware CORS à l’application FastAPI.
    
    :param cors_origins_autorisées: liste (ou séquence) d’origines autorisées (ex. ["https://exemple.com", ...])
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_origin_autorisées),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def _enregistrer_routers(app: FastAPI) -> None:
    app.include_router(routesActeurs.router)
    app.include_router(routesDocuments.router)
    app.include_router(routesOrganes.router)

def _définir_redirection_défaut_vers_la_documentation(app) :
    """
    Redirige la route racine vers la documentation ("/docs").
    "include_in_schema=False" permet de ne pas lister cette route dans la doc.
    """
    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/docs")

def créer_instance_application() -> FastAPI:
    app = FastAPI(default_response_class=ORJSONResponse)

    _configurer_cors(app, settings.effective_cors_allowed_origins)
    _enregistrer_routers(app)
    _définir_redirection_défaut_vers_la_documentation(app)
    _gestionnaire_exceptions.configurer_réponses_par_types_d_exceptions(app)

    return app

app = créer_instance_application()