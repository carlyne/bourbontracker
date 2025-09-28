from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, AliasChoices, Field

from src.metier.document.objet.cycleDeVie.cycleDeVie import CycleDeVie
from src.metier.document.objet.titre import Titres
from src.metier.acteur.objet.acteurDocument import ActeurDocument

class DocumentReponse(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True
    )

    cycle_de_vie: Optional[CycleDeVie] = None
    titres: Optional[Titres] = None
    auteurs: Optional[List[ActeurDocument]] = Field(
        default=None,
        validation_alias=AliasChoices("acteurs_documents", "auteurs"),
    )