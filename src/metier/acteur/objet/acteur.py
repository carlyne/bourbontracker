from __future__ import annotations
from typing import Optional, List, Any
from typing_extensions import Annotated
from datetime import date
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from json import loads

from src.metier._validators import NilableStr

StrEmptyAsNone = Annotated[Optional[str], BeforeValidator(lambda v: None if v in ("", None) else str(v))]

# --- Sous-modèles ---

class UidActeur(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True, serialize_by_alias=True)
    xmlns_xsi: Optional[str] = Field(alias="@xmlns:xsi", default=None)
    xsi_type: Optional[str]  = Field(alias="@xsi:type", default=None)
    text: Optional[str]      = Field(alias="#text", default=None)

class Ident(BaseModel):
    model_config = ConfigDict(extra="ignore")
    civ: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None
    alpha: Optional[str] = None
    trigramme: NilableStr = None

class InfoNaissance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    dateNais: Optional[date] = None
    villeNais: Optional[str] = None
    depNais: Optional[str] = None
    paysNais: Optional[str] = None

class DateDeces(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    xmlns_xsi: Optional[str] = Field(alias="@xmlns:xsi", default=None)
    xsi_nil: Optional[str]   = Field(alias="@xsi:nil", default=None)

class EtatCivil(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ident: Optional[Ident] = None
    infoNaissance: Optional[InfoNaissance] = None
    dateDeces: Optional[DateDeces] = None

class SocProcINSEE(BaseModel):
    model_config = ConfigDict(extra="ignore")
    catSocPro: Optional[str] = None
    famSocPro: Optional[str] = None

class Profession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    libelleCourant: Optional[str] = None
    socProcINSEE: Optional[SocProcINSEE] = None

class Adresse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    xmlns_xsi: Optional[str] = Field(alias="@xmlns:xsi", default=None)
    xsi_type: Optional[str]  = Field(alias="@xsi:type", default=None)
    uid: Optional[str] = None
    type: Optional[str] = None
    typeLibelle: Optional[str] = None
    poids: Optional[str] = None
    adresseDeRattachement: Optional[Any] = None
    intitule: Optional[str] = None
    numeroRue: Optional[str] = None
    nomRue: Optional[str] = None
    complementAdresse: Optional[str] = None
    codePostal: Optional[str] = None
    ville: Optional[str] = None
    valElec: Optional[str] = None  # pour sites web, twitter, e-mail

class Adresses(BaseModel):
    model_config = ConfigDict(extra="ignore")
    adresse: Optional[List[Adresse] | Adresse] = None

    @field_validator("adresse", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        if v is None:
            return None
        return v if isinstance(v, list) else [v]

class InfosQualite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    codeQualite: Optional[str] = None
    libQualite: Optional[str] = None
    libQualiteSex: Optional[str] = None

class OrganesRef(BaseModel):
    model_config = ConfigDict(extra="ignore")
    organeRef: Optional[str] = None

class LieuElection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    region: Optional[str] = None
    regionType: Optional[str] = None
    departement: Optional[str] = None
    numDepartement: Optional[str] = None
    numCirco: Optional[str] = None

class Election(BaseModel):
    model_config = ConfigDict(extra="ignore")
    lieu: Optional[LieuElection] = None
    causeMandat: Optional[str] = None
    refCirconscription: Optional[str] = None

class Suppleant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None
    suppleantRef: Optional[str] = None

class Suppleants(BaseModel):
    model_config = ConfigDict(extra="ignore")
    suppleant: Optional[List[Suppleant] | Suppleant] = None

    @field_validator("suppleant", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        if v is None:
            return None
        return v if isinstance(v, list) else [v]

class Mandature(BaseModel):
    model_config = ConfigDict(extra="ignore")
    datePriseFonction: Optional[date] = None
    causeFin: Optional[str] = None
    premiereElection: Optional[str] = None
    placeHemicycle: Optional[str] = None
    mandatRemplaceRef: Optional[str] = None

class Collaborateur(BaseModel):
    model_config = ConfigDict(extra="ignore")
    qualite: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None

class Collaborateurs(BaseModel):
    model_config = ConfigDict(extra="ignore")
    collaborateur: Optional[List[Collaborateur] | Collaborateur] = None

    @field_validator("collaborateur", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        if v is None:
            return None
        return v if isinstance(v, list) else [v]

class Mandat(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True, serialize_by_alias=True)

    xmlns_xsi: Optional[str] = Field(alias="@xmlns:xsi", default=None)
    xsi_type: Optional[str]  = Field(alias="@xsi:type",  default=None)

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
    organes: Optional[OrganesRef] = None

    suppleants: Optional[Suppleants] = None
    chambre: Optional[Any] = None
    election: Optional[Election] = None
    mandature: Optional[Mandature] = None
    collaborateurs: Optional[Collaborateurs] = None

class Mandats(BaseModel):
    model_config = ConfigDict(extra="ignore")
    mandat: Optional[List[Mandat] | Mandat] = None

    @field_validator("mandat", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        if v is None:
            return None
        return v if isinstance(v, list) else [v]

class Acteur(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True, serialize_by_alias=True)

    xmlns: Optional[str] = Field(alias="@xmlns", default=None)
    uid: Optional[UidActeur] = None
    etatCivil: Optional[EtatCivil] = None
    profession: Optional[Profession] = None
    uri_hatvp: Optional[str] = None
    adresses: Optional[Adresses] = None
    mandats: Optional[Mandats] = None
    uri_hatvp: NilableStr = None

    @field_validator("uid", mode="before")
    @classmethod
    def _wrap_uid(cls, v):
        if isinstance(v, str):
            return {"#text": v}
        return v

def _normalize_xmlish(obj):
    if isinstance(obj, dict):
        if "@xsi:nil" in obj:           
            from src.metier._validators import _xmlish_to_scalar
            return _xmlish_to_scalar(obj)   
        return {k: _normalize_xmlish(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_xmlish(x) for x in obj]
    return obj

def parse_acteur_depuis_fichier_json(payload: dict | str) -> Acteur:
    racine = loads(payload) if isinstance(payload, str) else payload

    if "acteur" not in racine:
        raise ValueError("Clé 'acteur' absente du JSON")
    
    donnée = racine["acteur"]
    donnée = _normalize_xmlish(donnée)
    
    return Acteur.model_validate(donnée)


