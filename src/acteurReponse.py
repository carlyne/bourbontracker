from __future__ import annotations

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator

class UidReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    text: str = Field(alias="#text")

class IdentReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    civ: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None

class EtatCivilReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    ident: Optional[IdentReponse] = None

class SocProcINSEEReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    catSocPro: Optional[str] = None
    famSocPro: Optional[str] = None

class ProfessionReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    libelleCourant: Optional[str] = None
    socProcINSEE: Optional[SocProcINSEEReponse] = None

class LieuReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    region: Optional[str] = None
    regionType: Optional[str] = None
    departement: Optional[str] = None
    numDepartement: Optional[str] = None
    numCirco: Optional[str] = None

class ElectionReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    lieu: Optional[LieuReponse] = None
    causeMandat: Optional[str] = None
    refCirconscription: Optional[str] = None

class MandatureReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    datePriseFonction: Optional[date] = None
    causeFin: Optional[str] = None
    premiereElection: Optional[str] = None
    placeHemicycle: Optional[str] = None
    mandatRemplaceRef: Optional[str] = None

class CollaborateurReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    qualite: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None

class CollaborateursReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    collaborateur: List[CollaborateurReponse] = Field(default_factory=list)

class SuppleantReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None
    suppleantRef: Optional[str] = None

class SuppleantsReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    suppleant: List[SuppleantReponse] = Field(default_factory=list)

    @field_validator("suppleant", mode="before")
    @classmethod
    def _coerce_list(cls, v):
        if v is None:
            return []
        return v if isinstance(v, list) else [v]

class ViMoDeReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    dateDebut: Optional[date] = None
    dateAgrement: Optional[date] = None
    dateFin: Optional[date] = None

class OrganeDetailReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    #uid: str
    #codeType: Optional[str] = None
    libelle: Optional[str] = None
    #viMoDe: Optional[ViMoDeReponse] = None
    #organeParent: Optional[str] = None
    #preseance: Optional[str] = None
    #organePrecedentRef: Optional[str] = None

class OrganesReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    #organeRef: Optional[str] = None
    detail: Optional[OrganeDetailReponse] = None

class InfosQualiteReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    codeQualite: Optional[str] = None

class MandatReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    #uid: Optional[str] = None
    #acteurRef: Optional[str] = None
    legislature: Optional[str] = None
    #typeOrgane: Optional[str] = None
    dateDebut: Optional[date] = None
    #datePublication: Optional[date] = None
    dateFin: Optional[date] = None
    #preseance: Optional[str] = None

    #infosQualite: Optional[InfosQualiteReponse] = None
    organes: Optional[OrganesReponse] = None
    #suppleants: Optional[SuppleantsReponse] = None
    #chambre: Optional[str] = None
    #election: Optional[ElectionReponse] = None
    #mandature: Optional[MandatureReponse] = None
    #collaborateurs: Optional[CollaborateursReponse] = None

class MandatsReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    mandat: List[MandatReponse] = Field(default_factory=list)

class ActeurReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    #uid: UidReponse
    etatCivil: Optional[EtatCivilReponse] = None
    #profession: Optional[ProfessionReponse] = None
    url_fiche_acteur: Optional[HttpUrl] = Field(default=None, alias="uri_hatvp")
    mandats: Optional[MandatsReponse] = None