from collections.abc import Sequence
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.api import gestionnaireDesExceptions
from src.api.routes import routesActeurs, routesDocuments, routesOrganes

def _configurer_cors(app: FastAPI, cors_origin_autorisées: Sequence[str]) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_origin_autorisées),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def _enregistrer_les_routes(app: FastAPI) -> None:
    app.include_router(routesActeurs.router)
    app.include_router(routesDocuments.router)
    app.include_router(routesOrganes.router)

# ---

def creer_application(cors_origins_autorisées: Sequence[str] | None = None) -> FastAPI:
    app = FastAPI(default_response_class=ORJSONResponse)

    # http://localhost:8081 : url du front en local
    _configurer_cors(app, cors_origins_autorisées or ("http://localhost:8081",))
    
    _enregistrer_les_routes(app)
    
    gestionnaireDesExceptions.enregistrer_réponses_par_type_d_exceptions(app)

    return app

app = creer_application()