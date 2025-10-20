from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

from src.metier import _utilitaire

class ViMoDe(BaseModel):
    """
    Vie Mort et Décomposition
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)
    
    dateDebut: Optional[date] = None
    dateAgrement: Optional[date] = None
    dateFin: Optional[date] = None

class Organe(BaseModel):
    """
    Schémas : https://www.assemblee-nationale.fr/opendata/Schemas_Entites/AMO/Schemas_Organes.html
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)
    
    uid: str
    codeType: Optional[str] = None
    libelle: Optional[str] = None
    libelleEdition: Optional[str] = None
    libelleAbrege: Optional[str] = None
    libelleAbrev: Optional[str] = None
    viMoDe: Optional[ViMoDe] = None
    organeParent: Optional[str] = None
    preseance: Optional[str] = None
    organePrecedentRef: Optional[str] = None


def parser_organe_depuis_payload(data: Dict[str, Any]) -> Organe:
    return _utilitaire.parser_depuis_payload(data, Organe, "organe")