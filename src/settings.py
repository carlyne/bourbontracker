from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["local", "render"] = Field(
        default="local",
        description="Environnement de déploiement courant.",
        validation_alias=AliasChoices("APP_ENVIRONMENT", "ENVIRONMENT"),
    )
    database_url: str = Field(
        ...,
        description="URL de connexion SQLAlchemy (sync) vers PostgreSQL.",
        validation_alias="DATABASE_URL",
    )
    cors_allowed_origins: list[str] = Field(
        default_factory=list,
        description="Origines autorisées pour le CORS.",
        validation_alias=AliasChoices(
            "APP_CORS_ALLOWED_ORIGINS",
            "CORS_ALLOWED_ORIGINS",
        ),
    )
    render_app_url: HttpUrl | None = Field(
        default="https://votre-service.onrender.com",
        description="URL publique de l'application lorsqu'elle est déployée sur Render.",
        validation_alias=AliasChoices(
            "APP_RENDER_APP_URL",
            "RENDER_EXTERNAL_URL",
        ),
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @property
    def effective_cors_allowed_origins(self) -> list[str]:
        if self.cors_allowed_origins:
            return self.cors_allowed_origins

        if self.environment == "render":
            return [str(self.render_app_url)] if self.render_app_url else []

        return ["http://localhost:8081"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()