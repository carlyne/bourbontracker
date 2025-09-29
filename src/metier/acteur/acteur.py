from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator

class Uid(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    text: str = Field(alias='#text')

class Ident(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    civ: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None

class InfoNaissance(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    dateNais: Optional[date] = None
    villeNais: Optional[str] = None
    depNais: Optional[str] = None
    paysNais: Optional[str] = None

class DateDeces(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    xmlns_xsi: Optional[str] = Field(default=None, alias='@xmlns:xsi')
    xsi_nil: Optional[bool] = Field(default=None, alias='@xsi:nil')

    @field_validator('xsi_nil', mode='before')
    @classmethod
    def _to_bool(cls, v):
        if isinstance(v, str):
            return v.lower() == "true"
        return v

class EtatCivil(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    ident: Optional[Ident] = None
    infoNaissance: Optional[InfoNaissance] = None
    dateDeces: Optional[DateDeces] = None

class SocProcINSEE(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    catSocPro: Optional[str] = None
    famSocPro: Optional[str] = None

class Profession(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    libelleCourant: Optional[str] = None
    socProcINSEE: Optional[SocProcINSEE] = None

# ---------- Mandats

class Lieu(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    region: Optional[str] = None
    regionType: Optional[str] = None
    departement: Optional[str] = None
    numDepartement: Optional[str] = None
    numCirco: Optional[str] = None

class Election(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    lieu: Optional[Lieu] = None
    causeMandat: Optional[str] = None
    refCirconscription: Optional[str] = None

class Mandature(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    datePriseFonction: Optional[date] = None
    causeFin: Optional[str] = None
    premiereElection: Optional[str] = None
    placeHemicycle: Optional[str] = None
    mandatRemplaceRef: Optional[str] = None


class Collaborateur(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    qualite: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None

class Collaborateurs(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    collaborateur: List[Collaborateur] = Field(default_factory=list)

class Suppleant(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None
    suppleantRef: Optional[str] = None

class Suppleants(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    suppleant:List[Suppleant] = Field(default_factory=list)

    @field_validator("suppleant", mode="before")
    @classmethod
    def _coerce_list(coercition, valeur):
        if valeur is None:
            return []
        if isinstance(valeur, list):
            return valeur
        return [valeur]

class InfosQualite(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    codeQualite: Optional[str] = None
    libQualite: Optional[str] = None
    libQualiteSex: Optional[str] = None

class Organes(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    organeRef: Optional[str] = None

class Mandat(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    uid: Optional[str] = None
    acteurRef: Optional[str] = None
    legislature: Optional[str] = None
    typeOrgane: Optional[str] = None
    dateDebut: Optional[date] = None
    datePublication: Optional[date] = None
    dateFin: Optional[date] = None
    preseance: Optional[str] = None
    nominPrincipale: Optional[str] = None

    infosQualite: Optional[InfosQualite] = None
    organes: Optional[Organes] = None
    suppleants: Optional[Suppleants] = None
    chambre: Optional[str] = None
    election: Optional[Election] = None
    mandature: Optional[Mandature] = None
    collaborateurs: Optional[Collaborateurs] = None


class Mandats(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    mandat: List[Mandat] = Field(default_factory=list)

class Acteur(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    uid: Uid
    etatCivil: Optional[EtatCivil] = None
    profession: Optional[Profession] = None
    url_fiche_acteur: Optional[HttpUrl] = Field(default=None, alias='uri_hatvp')
    mandats: Optional[Mandats] = None

def parse_acteur_depuis_fichier_json(donnée: Dict[str, Any]) -> Acteur:
    return Acteur.model_validate(donnée["acteur"])