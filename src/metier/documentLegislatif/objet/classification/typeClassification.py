from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TypeClassification(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: Optional[str] = None
    libelle: Optional[str] = None