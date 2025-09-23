from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.metier.documentLegislatif.objet.classification.typeClassification import TypeClassification
from src.metier.documentLegislatif.objet.classification.sousType import SousType
from src.metier.documentLegislatif.objet.classification.famille.famille import Famille

class Classification(BaseModel):
    model_config = ConfigDict(extra="ignore")

    famille: Optional[Famille] = None
    type: Optional[TypeClassification] = None
    sous_type: Optional[SousType] = Field(alias="sousType", default=None)
    statut_adoption: Optional[str] = Field(alias="statutAdoption", default=None)