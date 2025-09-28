from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.metier.document.objet.cycleDeVie.chrono import Chrono

class CycleDeVie(BaseModel):
    model_config = ConfigDict(extra="ignore")
    chrono: Optional[Chrono] = None 