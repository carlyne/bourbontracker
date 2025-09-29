from __future__ import annotations
from datetime import date
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

class ViMoDe(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    dateDebut: Optional[date] = None
    dateAgrement: Optional[date] = None
    dateFin: Optional[date] = None

class Organe(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

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


def parse_organe_depuis_fichier_json(data: Dict[str, Any]) -> Organe:
    payload = data.get("organe", data)
    return Organe.model_validate(payload)
