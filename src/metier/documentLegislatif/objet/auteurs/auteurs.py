from __future__ import annotations
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator

from src.metier.documentLegislatif.objet.auteurs.auteur import Auteur

class Auteurs(BaseModel):
    model_config = ConfigDict(extra="ignore")

    auteur: Optional[List[Auteur] | Auteur] = None

    @field_validator("auteur", mode="before")
    @classmethod
    def _wrap_singleton(cls, v: Any):
        if v is None:
            return None
        return v if isinstance(v, list) else [v]