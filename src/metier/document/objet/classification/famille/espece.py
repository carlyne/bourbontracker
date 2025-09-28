from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class Espece(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: Optional[str] = None
    libelle: Optional[str] = None
    libelle_edition: Optional[str] = Field(alias="libelleEdition", default=None)
