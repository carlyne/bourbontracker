from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.metier.documentLegislatif.objet.classification.famille.depot import Depot
from src.metier.documentLegislatif.objet.classification.famille.classe import Classe
from src.metier.documentLegislatif.objet.classification.famille.espece import Espece

class Famille(BaseModel):
    model_config = ConfigDict(extra="ignore")

    depot: Optional[Depot] = None
    classe: Optional[Classe] = None
    espece: Optional[Espece] = None