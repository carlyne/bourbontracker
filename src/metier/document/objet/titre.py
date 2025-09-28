from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Titres(BaseModel):
    model_config = ConfigDict(extra="ignore")

    titre_principal: Optional[str] = Field(alias="titrePrincipal", default=None)
    titre_principal_court: Optional[str] = Field(alias="titrePrincipalCourt", default=None)