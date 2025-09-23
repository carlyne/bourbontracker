from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.metier.deputeEnExercice.objet.deputeEnExercice import EtatCivil, Profession

class DeputeEnExerciceReponse(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True
    )

    uid: Optional[str] = None
    etatCivil: Optional[EtatCivil] = None
    profession: Optional[Profession] = None
