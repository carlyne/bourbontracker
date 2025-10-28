from __future__ import annotations

from datetime import date
from typing import (
    Any, 
    Dict, 
    Optional, 
    List
)
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    HttpUrl,
    field_validator,
    FieldValidationInfo,
    model_validator,
)

from src.metier.organe.organe import Organe
from src.metier import _utilitaire


class Uid(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    text: str = Field(alias="#text")

    @model_validator(mode="before")
    @classmethod
    def _coerce_str_to_alias_dict(cls, v):
        if isinstance(v, str):
            return {"#text": v}
        if isinstance(v, dict) and "text" in v and "#text" not in v:
            return {"#text": v["text"]}
        return v


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

    @field_validator("dateNais", mode="before")
    @classmethod
    def _nilable_date(cls, v):
        return _utilitaire.date_ou_none(v)

    @field_validator("villeNais", "depNais", "paysNais", mode="before")
    @classmethod
    def _nilable_str(cls, v):
        return _utilitaire.nil_ou_text(v)


class DateDeces(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    xmlns_xsi: Optional[str] = Field(default=None, alias="@xmlns:xsi")
    xsi_nil: Optional[bool] = Field(default=None, alias="@xsi:nil")
    value: Optional[date] = Field(default=None, alias="#text")

    @field_validator("xsi_nil", mode="before")
    @classmethod
    def _to_bool(cls, v):
        if isinstance(v, str):
            return v.lower() == "true"
        return v

    @field_validator("value", mode="before")
    @classmethod
    def _nilable_date(cls, v):
        return _utilitaire.date_ou_none(v)


class EtatCivil(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    ident: Optional[Ident] = None
    infoNaissance: Optional[InfoNaissance] = None
    dateDeces: Optional[DateDeces] = None

    @field_validator("dateDeces", mode="before")
    @classmethod
    def _string_to_date_deces(cls, value: Any):
        """Accepte un champ `dateDeces` fourni directement en chaîne ISO."""
        if isinstance(value, str):
            valeur_normalisee = value.strip()
            if not valeur_normalisee:
                return None
            return {"#text": valeur_normalisee}
        return value

class SocProcINSEE(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    catSocPro: Optional[str] = None
    famSocPro: Optional[str] = None

    @field_validator("catSocPro", "famSocPro", mode="before")
    @classmethod
    def _nilable_str(cls, v):
        return _utilitaire.nil_ou_text(v)


class Profession(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    libelleCourant: Optional[str] = None
    socProcINSEE: Optional[SocProcINSEE] = None

    @field_validator("libelleCourant", mode="before")
    @classmethod
    def _nilable_str(cls, v):
        return _utilitaire.nil_ou_text(v)


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

    @field_validator("datePriseFonction", mode="before")
    @classmethod
    def _nilable_date(cls, v):
        return _utilitaire.date_ou_none(v)


class Collaborateur(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    qualite: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None

    @field_validator("dateDebut", "dateFin", mode="before")
    @classmethod
    def _nilable_date(cls, v):
        return _utilitaire.date_ou_none(v)


class Collaborateurs(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    collaborateur: List[Collaborateur] = Field(default_factory=list)

    @field_validator("collaborateur", mode="before")
    @classmethod
    def _coerce_list(cls, v):
        return _utilitaire.transformer_en_liste(v)


class Suppleant(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None
    suppleantRef: Optional[str] = None

    @field_validator("dateDebut", "dateFin", mode="before")
    @classmethod
    def _nilable_date(cls, v):
        return _utilitaire.date_ou_none(v)


class Suppleants(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    suppleant: List[Suppleant] = Field(default_factory=list)

    @field_validator("suppleant", mode="before")
    @classmethod
    def _coerce_list(cls, v):
        return _utilitaire.transformer_en_liste(v)


class InfosQualite(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    codeQualite: Optional[str] = None
    libQualite: Optional[str] = None
    libQualiteSex: Optional[str] = None


class Organes(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    organeRef: Optional[str] = None
    detail: Optional[Organe] = None

    @field_validator("organeRef", mode="before")
    @classmethod
    def _nilable_str(cls, v):
        return _utilitaire.nil_ou_text(v)


class Mandat(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore", 
        from_attributes=True
    )

    uid: Optional[str] = None
    acteurRef: Optional[str] = None
    legislature: Optional[str] = None
    # GP : Groupe Politique
    # GE : Groupoe d'Etude
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

    @field_validator(
        "dateDebut",
        "datePublication",
        "dateFin",
        mode="before",
    )
    @classmethod
    def _nilable_date(cls, v):
        return _utilitaire.date_ou_none(v)

    @field_validator("collaborateurs", "suppleants", mode="before")
    @classmethod
    def _coerce_nested_collections(cls, v, info: FieldValidationInfo):
        if isinstance(v, list):
            clé = "collaborateur" if info.field_name == "collaborateurs" else "suppleant"
            valeurs = [element for element in v if element is not None]
            return {clé: valeurs}
        return v


class Mandats(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
         extra="ignore", 
        from_attributes=True
    )

    mandat: List[Mandat] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalize_input(cls, v):
        if v is None:
            return {"mandat": []}
        if isinstance(v, dict):
            return v
        try:
            return {"mandat": [x for x in v if x is not None]}
        except TypeError:
            return {"mandat": [v]}


class Acteur(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore", 
        from_attributes=True
    )

    uid: Uid
    etatCivil: Optional[EtatCivil] = None
    profession: Optional[Profession] = None
    url_fiche_acteur: Optional[HttpUrl] = Field(default=None, alias="uri_hatvp")
    mandats: Optional[Mandats] = None

    @field_validator("url_fiche_acteur", mode="before")
    @classmethod
    def _nilable_url(cls, v):
        return _utilitaire.nil_ou_text(v)

def parser_acteur_depuis_payload(data: Dict[str, Any]) -> Acteur:
    return _utilitaire.parser_depuis_payload(data, Acteur, "acteur")