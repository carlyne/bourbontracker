from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.metier.acteur.objet.acteur import EtatCivil, Profession

class ActeurReponse(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True
    )

    uid: Optional[str] = None
    etatCivil: Optional[EtatCivil] = None
    profession: Optional[Profession] = None
