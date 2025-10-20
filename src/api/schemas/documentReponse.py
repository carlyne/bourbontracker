from __future__ import annotations

from typing_extensions import Annotated
from typing import (
    List, 
    Optional
)
from pydantic import (
    AwareDatetime, 
    BaseModel, 
    BeforeValidator, 
    Field,
    ConfigDict
)

from src.api.schemas.acteurReponse import ActeurReponse

def _transformer_en_liste(valeur):
    if valeur is None:
        return []
    return valeur if isinstance(valeur, list) else [valeur]

class ChronoReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    date_creation: Optional[AwareDatetime] = Field(
        default=None,
        alias="dateCreation",
        description="Date de création du document dans le référentiel législatif."
    )
    date_depot: Optional[AwareDatetime] = Field(
        default=None,
        alias="dateDepot",
        description="Date officielle du dépôt du document à l’Assemblée nationale."
    )
    date_publication: Optional[AwareDatetime] = Field(
        default=None,
        alias="datePublication",
        description="Date de publication du document (Journal Officiel, base législative)."
    )

class CycleDeVieReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    chrono: Optional[ChronoReponse] = Field(
        default=None,
        alias="chrono",
        description="Bloc de données temporelles du document."
    )

class TitresReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )
        
    titre_principal: Optional[str] = Field(
        default=None,
        alias="titrePrincipal",
        description="Titre officiel du document législatif."
    )

class ActeurRefReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    detail: Optional[ActeurReponse] = Field(
        default=None,
        alias="acteur_detail",
        description="Détails sur l’acteur associé à l’auteur du document."
    )

class AuteurReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )
    
    acteur: Optional[ActeurRefReponse] = Field(
        default=None,
        alias="acteur",
        description="Acteur (député, groupe, organe) ayant déposé le document."
    )

class AuteursReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    auteur: List[AuteurReponse] = Field(
        default_factory=list,
        alias="auteur",
        description="Liste des auteurs associés au document."
    )

class NoticeReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    formule: Optional[str] = Field(
        default=None,
        alias="formule",
        description="Texte de la notice accompagnant le document législatif."
    )

class OrganesReferentsReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    organe_ref: Annotated[List[str], BeforeValidator(_transformer_en_liste)] = Field(
        default_factory=list,
        alias="organeRef",
        description="Liste des identifiants d’organes parlementaires référents."
    )

class DocumentReponse(BaseModel):
    """
    Documentation officielle des termes métier : https://www.assemblee-nationale.fr/opendata/index_pub.html
    """
        
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    uid: Optional[str] = Field(
        default=None,
        alias="uid",
        description="Identifiant unique du document dans le référentiel législatif."
    )

    legislature: Optional[str] = Field(
        default=None,
        alias="legislature",
        description="Numéro de la législature pendant laquelle le document a été produit."
    )

    cycle_de_vie: Optional[CycleDeVieReponse] = Field(
        default=None,
        alias="cycleDeVie",
        description="Cycle de vie complet du document (création, dépôt, publication)."
    )

    titres: Optional[TitresReponse] = Field(
        default=None,
        alias="titres",
        description="Titres principaux ou alternatifs du document législatif."
    )

    auteurs: Optional[AuteursReponse] = Field(
        default=None,
        alias="auteurs",
        description="Liste des auteurs du document."
    )

    notice: Optional[NoticeReponse] = Field(
        default=None,
        alias="notice",
        description="Notice explicative liée au document législatif."
    )
    
    organes_referents: Optional[OrganesReferentsReponse] = Field(
        default=None,
        alias="organesReferents",
        description="Organes parlementaires responsables du suivi du document."
    )
