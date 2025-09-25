from __future__ import annotations

from datetime import date
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

# ---------- utilitaires ----------

def _is_nil_dict(v: Any) -> bool:
    return isinstance(v, dict) and v.get("@xsi:nil") in ("true", True)

def _text_or_none(v: Any) -> Any:
    if isinstance(v, dict):
        if _is_nil_dict(v):
            return None
        if "#text" in v:
            return v["#text"]
    return v

def _normalize(obj: Any) -> Any:
    obj = _text_or_none(obj)
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize(x) for x in obj]
    return obj

def _ensure_list(x: Any) -> list:
    if not x:
        return []
    return x if isinstance(x, list) else [x]

def _get(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

# ---------- sous-objets ----------

class Identite(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    civilite: Optional[str] = Field(alias="civ", default=None)
    prenom: Optional[str] = None
    nom: Optional[str] = None
    alpha: Optional[str] = None
    trigramme: Optional[str] = None

class InfoNaissance(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    date_naissance: Optional[date] = Field(alias="dateNais", default=None)
    ville: Optional[str] = Field(alias="villeNais", default=None)
    departement: Optional[str] = Field(alias="depNais", default=None)
    pays: Optional[str] = Field(alias="paysNais", default=None)

    @field_validator("date_naissance", mode="before")
    @classmethod
    def _parse_date(cls, v):
        if isinstance(v, str) and v:
            return date.fromisoformat(v)
        return v

class Adresse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    uid: Optional[str] = None
    type_libelle: Optional[str] = Field(alias="typeLibelle", default=None)
    val_elec: Optional[str] = Field(alias="valElec", default=None)

    intitule: Optional[str] = None
    numero_rue: Optional[str] = Field(alias="numeroRue", default=None)
    nom_rue: Optional[str] = Field(alias="nomRue", default=None)
    complement_adresse: Optional[str] = Field(alias="complementAdresse", default=None)
    code_postal: Optional[str] = Field(alias="codePostal", default=None)
    ville: Optional[str] = None

class Mandat(BaseModel):
    """
    Note: certains mandats (e.g. MandatMission_Type) exposent organes.organeRef
    comme *liste* de références. On normalise en une liste de str.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    uid: str
    acteur_ref: Optional[str] = Field(alias="acteurRef", default=None)
    legislature: Optional[str] = None
    type_organe: Optional[str] = Field(alias="typeOrgane", default=None)

    date_debut: Optional[date] = Field(alias="dateDebut", default=None)
    date_publication: Optional[date] = Field(alias="datePublication", default=None)
    date_fin: Optional[date] = Field(alias="dateFin", default=None)

    # <<--------- changement ici: toujours une liste --------->>
    organe_refs: List[str] = Field(default_factory=list)

    # champs qualité
    code_qualite: Optional[str] = None
    lib_qualite: Optional[str] = None
    lib_qualite_sex: Optional[str] = None

    # optionnel pour MandatMission_Type
    libelle: Optional[str] = None

    @field_validator("date_debut", "date_publication", "date_fin", mode="before")
    @classmethod
    def _parse_dates(cls, v):
        if isinstance(v, str) and v:
            return date.fromisoformat(v)
        return v

    @classmethod
    def from_json(cls, payload: dict) -> "Mandat":
        # organes.organeRef peut être str ou list[str]
        raw_org = _get(payload, "organes", "organeRef")
        org_list = _ensure_list(_normalize(raw_org))
        org_list = [str(x) for x in org_list if isinstance(x, (str, int)) and str(x)]

        iq = _get(payload, "infosQualite") or {}
        return cls.model_validate({
            **payload,
            "organe_refs": org_list,
            "code_qualite": iq.get("codeQualite"),
            "lib_qualite": iq.get("libQualite"),
            "lib_qualite_sex": iq.get("libQualiteSex"),
            # MandatMission_Type fournit parfois un "libelle" au même niveau
            "libelle": payload.get("libelle"),
        })

class ActeurDocument(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    uid: str = Field()
    identite: Optional[Identite] = None
    naissance: Optional[InfoNaissance] = None

    profession: Optional[str] = None
    url_hatvp: Optional[str] = Field(alias="uri_hatvp", default=None)

    email: Optional[EmailStr] = None
    site: Optional[str] = None
    twitter: Optional[str] = None

    adresses: List[Adresse] = Field(default_factory=list)
    mandats: List[Mandat] = Field(default_factory=list)

    @classmethod
    def from_acteur_json(cls, payload: dict) -> "ActeurDocument":
        normalized = _normalize(payload or {})
        a = normalized.get("acteur") or {}

        uid = _get(a, "uid") or ""
        ident = _get(a, "etatCivil", "ident") or {}
        naissance = _get(a, "etatCivil", "infoNaissance") or {}

        profession = _get(a, "profession", "libelleCourant")

        adrs_raw = _ensure_list(_get(a, "adresses", "adresse"))
        adresses = [Adresse.model_validate(x) for x in adrs_raw]

        email = site = twitter = None
        for item in adrs_raw:
            tlib = (item or {}).get("typeLibelle") or ""
            val = (item or {}).get("valElec")
            if not tlib or not val:
                continue
            low = tlib.casefold()
            if (("mèl" in low or "mel" in low) and email is None):
                email = val
            elif ("site" in low and site is None):
                site = val
            elif ("twitter" in low and twitter is None):
                twitter = val

        mandats_raw = _ensure_list(_get(a, "mandats", "mandat"))
        mandats = [Mandat.from_json(m) for m in mandats_raw]

        return cls(
            uid=uid,
            identite=Identite.model_validate(ident) if ident else None,
            naissance=InfoNaissance.model_validate(naissance) if naissance else None,
            profession=profession,
            url_hatvp=a.get("uri_hatvp"),
            email=email,
            site=site,
            twitter=twitter,
            adresses=adresses,
            mandats=mandats,
        )