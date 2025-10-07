"""FastAPI application entrypoint."""
from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.api import exceptions
from src.api.routes import acteurs, documents, organes


def create_app(allowed_origins: Sequence[str] | None = None) -> FastAPI:
    """Application factory used by ASGI servers and tests."""
    app = FastAPI(default_response_class=ORJSONResponse)

    _configure_cors(app, allowed_origins or ("http://localhost:8081",))
    _register_routes(app)
    exceptions.register_exception_handlers(app)

    return app


def _configure_cors(app: FastAPI, allowed_origins: Sequence[str]) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_routes(app: FastAPI) -> None:
    app.include_router(documents.router)
    app.include_router(acteurs.router)
    app.include_router(organes.router)


app = create_app()
