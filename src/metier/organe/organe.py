from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.metier import _utilitaire


class ViMoDe(BaseModel):
    """
    Vie Mort et Décomposition
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        from_attributes=True
    )

    dateDebut: Optional[date] = Field(default=None, alias="dateDebut")
    dateAgrement: Optional[date] = Field(default=None, alias="dateAgrement")
    dateFin: Optional[date] = Field(default=None, alias="dateFin")


class Organe(BaseModel):
    """
    Schémas : https://www.assemblee-nationale.fr/opendata/Schemas_Entites/AMO/Schemas_Organes.html
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        from_attributes=True
    )

    uid: str
    codeType: Optional[str] = Field(default=None, alias="codeType")
    libelle: Optional[str] = None
    libelleEdition: Optional[str] = Field(default=None, alias="libelleEdition")
    libelleAbrege: Optional[str] = Field(default=None, alias="libelleAbrege")
    libelleAbrev: Optional[str] = Field(default=None, alias="libelleAbrev")
    viMoDe: Optional[ViMoDe] = Field(default=None, alias="viMoDe")
    organeParent: Optional[str] = Field(default=None, alias="organeParent")
    preseance: Optional[str] = None
    organePrecedentRef: Optional[str] = Field(default=None, alias="organePrecedentRef")


def parser_organe_depuis_payload(data: Dict[str, Any]) -> Organe:
    return _utilitaire.parser_depuis_payload(data, Organe, "organe")
