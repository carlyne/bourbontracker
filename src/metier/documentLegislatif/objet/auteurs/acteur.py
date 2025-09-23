from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Acteur(BaseModel):
    model_config = ConfigDict(extra="ignore")

    acteur_ref: Optional[str] = Field(alias="acteurRef", default=None)
    qualite: Optional[str] = None