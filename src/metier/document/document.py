from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import Annotated
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator

from src.metier.acteur.acteur import Acteur as ActeurMetier
from src.metier import _utilitaire

_TransformerEnListe = BeforeValidator(_utilitaire.transformer_en_liste)

AwareDateTimeOrNone = Optional[AwareDatetime]


class OrganesReferents(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    organeRef: Annotated[List[str], _TransformerEnListe] = Field(default_factory=list)


class Depot(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    code: Optional[str] = None
    libelle: Optional[str] = None


class Classe(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    code: Optional[str] = None
    libelle: Optional[str] = None


class Espece(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    code: Optional[str] = None
    libelle: Optional[str] = None
    libelleEdition: Optional[str] = None


class Famille(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    depot: Optional[Depot] = None
    classe: Optional[Classe] = None
    espece: Optional[Espece] = None


class Type_(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    code: Optional[str] = None
    libelle: Optional[str] = None


class SousType(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    code: Optional[str] = None
    libelle: Optional[str] = None
    libelleEdition: Optional[str] = None


class Classification(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    famille: Optional[Famille] = None
    type_: Optional[Type_] = Field(default=None, alias="type")
    sousType: Optional[SousType] = None
    statutAdoption: Optional[Any] = None


class Chrono(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    dateCreation: AwareDateTimeOrNone = None
    dateDepot: AwareDateTimeOrNone = None
    datePublication: AwareDateTimeOrNone = None
    datePublicationWeb: AwareDateTimeOrNone = None


class CycleDeVie(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    chrono: Optional[Chrono] = None


class Titres(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    titrePrincipal: Optional[str] = None
    titrePrincipalCourt: Optional[str] = None


class Acteur(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    acteurRef: Optional[str] = None
    acteur_detail: Optional[ActeurMetier] = None
    qualite: Optional[str] = None


class Auteur(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    acteur: Optional[Acteur] = None


class Auteurs(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    auteur: Annotated[List[Auteur], _TransformerEnListe] = Field(default_factory=list)


class Notice(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore", from_attributes=True)

    numNotice: Optional[str] = None
    formule: Optional[str] = None
    adoptionConforme: Optional[str] = None


class Document(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True, from_attributes=True)

    uid: Optional[str] = None
    legislature: Optional[str] = None

    cycleDeVie: Optional[CycleDeVie] = None
    denominationStructurelle: Optional[str] = None
    provenance: Optional[str] = None
    titres: Optional[Titres] = None

    divisions: Optional[Any] = None
    dossierRef: Optional[str] = None
    redacteur: Optional[Any] = None

    classification: Optional[Classification] = None
    auteurs: Optional[Auteurs] = None
    correction: Optional[Any] = None
    notice: Optional[Notice] = None
    indexation: Optional[Any] = None
    organesReferents: Optional[OrganesReferents] = None


def parse_document_depuis_payload(data: Dict[str, Any]) -> Document:
    return _utilitaire.parser_depuis_payload(data, Document, "document")