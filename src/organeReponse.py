from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ViMoDeReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    dateDebut: Optional[date] = None
    dateAgrement: Optional[date] = None
    dateFin: Optional[date] = None

class OrganeReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    #uid: str
    #codeType: Optional[str] = None
    libelle: Optional[str] = None
    viMoDe: Optional[ViMoDeReponse] = None
    #organeParent: Optional[str] = None
    #preseance: Optional[str] = None
    #organePrecedentRef: Optional[str] = None