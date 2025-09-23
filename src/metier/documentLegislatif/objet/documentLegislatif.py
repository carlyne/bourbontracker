from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from src.metier.documentLegislatif.objet.cycleDeVie.cycleDeVie import CycleDeVie
from src.metier.documentLegislatif.objet.titre import Titres
from src.metier.documentLegislatif.objet.notice import Notice
from src.metier.documentLegislatif.objet.auteurs.auteurs import Auteurs
from src.metier.documentLegislatif.objet.classification.classification import Classification

class DocumentLegislatif(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True
    )

    uid: str
    legislature: Optional[str] = None

    cycle_de_vie: Optional[CycleDeVie] = Field(alias="cycleDeVie", default=None)

    denomination_structurelle: Optional[str] = Field(alias="denominationStructurelle", default=None)
    provenance: Optional[str] = None

    titres: Optional[Titres] = None
    divisions: Optional[Any] = None
    dossier_ref: Optional[str] = Field(alias="dossierRef", default=None)
    redacteur: Optional[Any] = None

    classification: Optional[Classification] = None
    auteurs: Optional[Auteurs] = None
    correction: Optional[Any] = None

    notice: Optional["Notice"] = None
    indexation: Optional[Any] = None

def parser(payload: dict | str) -> DocumentLegislatif:
    if isinstance(payload, str):
        from json import loads
        root = loads(payload)
    else:
        root = payload

    doc = root.get("document")
    if doc is None:
        raise ValueError("Clé 'document' absente du JSON")

    return DocumentLegislatif.model_validate(doc)
