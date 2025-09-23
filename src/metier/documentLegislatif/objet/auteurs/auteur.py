from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.metier.documentLegislatif.objet.auteurs.acteur import Acteur

class Auteur(BaseModel):
    model_config = ConfigDict(extra="ignore")

    acteur: Optional[Acteur] = None
