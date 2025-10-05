from __future__ import annotations

from typing_extensions import Annotated
from typing import List, Optional
from pydantic import AwareDatetime, BaseModel, BeforeValidator, ConfigDict

from src.acteurReponse import ActeurReponse

def _to_list(valeur):
    if valeur is None:
        return []
    return valeur if isinstance(valeur, list) else [valeur]

class ChronoReponse(BaseModel):
    dateCreation: Optional[AwareDatetime] = None
    dateDepot: Optional[AwareDatetime] = None
    datePublication: Optional[AwareDatetime] = None
    datePublicationWeb: Optional[AwareDatetime] = None

class CycleDeVieReponse(BaseModel):
    chrono: Optional[ChronoReponse] = None

class TitresReponse(BaseModel):
    titrePrincipal: Optional[str] = None
    titrePrincipalCourt: Optional[str] = None

class TypeReponse(BaseModel):
    libelle: Optional[str] = None

class SousTypeReponse(BaseModel):
    libelle: Optional[str] = None

class ClassificationReponse(BaseModel):
    type: Optional[TypeReponse] = None
    sousType: Optional[SousTypeReponse] = None
    statutAdoption: Optional[str] = None

class ActeurRefReponse(BaseModel):
    acteurRef: Optional[str] = None
    acteur_detail: Optional[ActeurReponse] = None
    qualite: Optional[str] = None

class AuteurReponse(BaseModel):
    acteur: Optional[ActeurRefReponse] = None

class AuteursReponse(BaseModel):
    auteur: List[AuteurReponse] = []

class NoticeReponse(BaseModel):
    formule: Optional[str] = None
    adoptionConforme: Optional[str] = None

class CosignataireReponse(BaseModel):
    acteur: Optional[ActeurRefReponse] = None
    dateCosignature: Optional[str] = None
    dateRetraitCosignature: Optional[str] = None

class CoSignatairesReponse(BaseModel):
    coSignataire: List[CosignataireReponse] = []

class AmendementsSeanceReponse(BaseModel):
    amendable: Optional[bool] = None

class OrganeRefCommissionReponse(BaseModel):
    organeRef: Optional[str] = None

class AmendementsCommissionReponse(BaseModel):
    commission: Optional[OrganeRefCommissionReponse] = None

class DepotAmendementsReponse(BaseModel):
    amendementsSeance: Optional[AmendementsSeanceReponse] = None
    amendementsCommission: Optional[AmendementsCommissionReponse] = None

class OrganesReferentsReponse(BaseModel):
    organeRef: Annotated[List[str], BeforeValidator(_to_list)] = []

class DocumentReponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uid: Optional[str] = None
    legislature: Optional[str] = None
    cycleDeVie: Optional[CycleDeVieReponse] = None
    denominationStructurelle: Optional[str] = None
    provenance: Optional[str] = None
    titres: Optional[TitresReponse] = None
    redacteur: Optional[str] = None
    classification: Optional[ClassificationReponse] = None
    auteurs: Optional[AuteursReponse] = None
    correction: Optional[str] = None
    notice: Optional[NoticeReponse] = None
    coSignataires: Optional[CoSignatairesReponse] = None
    depotAmendements: Optional[DepotAmendementsReponse] = None
    organesReferents: Optional[OrganesReferentsReponse] = None
