from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import Annotated

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator

from src.metier.acteur.acteur import Acteur as ActeurMetier
from src.metier import _utilitaire

_TransformerEnListe = BeforeValidator(_utilitaire.transformer_en_liste)

AwareDateTimeOrNone = Optional[AwareDatetime]

class Depot(BaseModel):
    code: Optional[str] = None
    libelle: Optional[str] = None

class Classe(BaseModel):
    code: Optional[str] = None
    libelle: Optional[str] = None

class Espece(BaseModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    libelleEdition: Optional[str] = None

class Famille(BaseModel):
    depot: Optional[Depot] = None
    classe: Optional[Classe] = None
    espece: Optional[Espece] = None

class Type_(BaseModel):
    code: Optional[str] = None
    libelle: Optional[str] = None

class SousType(BaseModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    libelleEdition: Optional[str] = None

class Classification(BaseModel):
    famille: Optional[Famille] = None
    type_: Optional[Type_] = Field(default=None, alias="type")
    sousType: Optional[SousType] = None
    statutAdoption: Optional[Any] = None

class Chrono(BaseModel):
    dateCreation: AwareDateTimeOrNone = None
    dateDepot: AwareDateTimeOrNone = None
    datePublication: AwareDateTimeOrNone = None
    datePublicationWeb: AwareDateTimeOrNone = None

class CycleDeVie(BaseModel):
    chrono: Optional[Chrono] = None

class Titres(BaseModel):
    titrePrincipal: Optional[str] = None
    titrePrincipalCourt: Optional[str] = None

class Acteur(BaseModel):
    acteurRef: Optional[str] = None
    acteur_detail: Optional[ActeurMetier] = None
    qualite: Optional[str] = None

class Auteur(BaseModel):
    acteur: Optional[Acteur] = None

class Auteurs(BaseModel):
    auteur: Annotated[List[Auteur], _TransformerEnListe] = Field(default_factory=list)

class Notice(BaseModel):
    numNotice: Optional[str] = None
    formule: Optional[str] = None
    adoptionConforme: Optional[str] = None

class Document(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

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

def parse_document_depuis_payload(data: Dict[str, Any]) -> Document:
    return _utilitaire.parser_depuis_payload(data, Document, "document")