from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ActeurDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")

    uid: str = Field()
    prenom: Optional[str] = None
    nom: Optional[str] = None
    civilite: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    twitter: Optional[str] = None

    @classmethod
    def from_acteur_json(cls, payload: dict) -> "ActeurDocument":
        a = payload.get("acteur", {})
        uid = (a.get("uid") or {}).get("#text") or ""
        ident = ((a.get("etatCivil") or {}).get("ident") or {})
        prenom = ident.get("prenom")
        nom = ident.get("nom")
        civilite = ident.get("civ")

        email = site = twitter = None
        adrs = ((a.get("adresses") or {}).get("adresse") or [])
        if isinstance(adrs, dict):
            adrs = [adrs]
        for item in adrs:
            tlib = item.get("typeLibelle", "")
            if not tlib:
                continue
            if "Mèl" in tlib and not email:
                email = item.get("valElec")
            elif "Site internet" in tlib and not site:
                site = item.get("valElec")
            elif "Twitter" in tlib and not twitter:
                twitter = item.get("valElec")

        return cls(uid=uid, prenom=prenom, nom=nom, civilite=civilite,
                   email=email, site=site, twitter=twitter)
