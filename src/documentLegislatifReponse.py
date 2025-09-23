from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.metier.documentLegislatif.objet.cycleDeVie.cycleDeVie import CycleDeVie
from src.metier.documentLegislatif.objet.titre import Titres
from src.metier.documentLegislatif.objet.auteurs.auteurs import Auteurs

class DocumentLegislatifReponse(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True
    )

    cycle_de_vie: Optional[CycleDeVie] = None
    titres: Optional[Titres] = None
    auteurs: Optional[Auteurs] = None