from __future__ import annotations

from datetime import date
from typing import (
    Optional, 
    List
)
from pydantic import (
    BaseModel, 
    Field, 
    ConfigDict, 
    HttpUrl
)

class UidReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        # ignore les champs supplémentaires lors des parsings
        extra="ignore"
    )

    text: str = Field(
        # indique que le champ ne peut pas être nul
        ...,
        alias="#text",
        description="identifiant unique de l'acteur"
    )

class IdentReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )

    civ: Optional[str] = Field(
        default=None,
        alias="civ",
        description="Civilité de l’acteur (ex. M., Mme)."
    )
    prenom: Optional[str] = Field(
        default=None,
        alias="prenom",
        description="Prénom de l’acteur tel que figurant dans les données de référence."
    )
    nom: Optional[str] = Field(
        default=None,
        alias="nom",
        description="Nom de famille de l’acteur tel que figurant dans les données de référence."
    )

class EtatCivilReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    ident: Optional[IdentReponse] = Field(
        default=None,
        alias="ident",
        description="Bloc d’identification de l’acteur, comprenant civilité, prénom et nom."
    )


class OrganeDetailReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    libelle: Optional[str] = Field(
        default=None,
        alias="libelle",
        description="Libellé (partiel ?) de l’organe. Ex : « Bretagne » pour le conseil régional de Bretagne"
    )

class OrganesReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    detail: Optional[OrganeDetailReponse] = Field(
        default=None,
        alias="detail",
        description="Détail de l’organe lié au mandat de l’acteur."
    )

class MandatReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )

    legislature: Optional[str] = Field(
        default=None,
        alias="legislature",
        description="Numéro de la législature durant laquelle le mandat est exercé (ex. '16')."
    )
    type_organe: Optional[str] = Field(
        default=None,
        alias="typeOrgane",
        description="Type d’organe concerné (ex. 'ASSEMBLEE', 'GROUPE_POLITIQUE')."
    )
    date_debut: Optional[date] = Field(
        default=None,
        alias="dateDebut",
        description="Date officielle de début du mandat."
    )
    date_fin: Optional[date] = Field(
        default=None,
        alias="dateFin",
        description="Date de fin du mandat (ou null si en cours)."
    )
    organes: Optional[OrganesReponse] = Field(
        default=None,
        alias="organes",
        description="Organe auquel le mandat rattache l’acteur."
    )

class MandatsReponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )

    mandat: List[MandatReponse] = Field(
        default_factory=list,
        alias="mandat",
        description="Liste des mandats successifs ou en cours détenus par l’acteur."
    )


class ActeurReponse(BaseModel):
    """
    Documentation officielle des champs : https://www.assemblee-nationale.fr/opendata/Schemas_Entites/AMO/Schemas_Acteurs.html#acteur
    """
        
    model_config = ConfigDict(
        populate_by_name=True, 
        extra="ignore"
    )

    uid: UidReponse

    etat_civil: Optional[EtatCivilReponse] = Field(
        default=None,
        alias="etatCivil",
        description="Données d’état civil de l’acteur"
    )

    url_fiche_acteur: Optional[HttpUrl] = Field(
        default=None,
        alias="uri_hatvp",
        description="URL de la fiche d’acteur"
    )

    mandats: Optional[MandatsReponse] = Field(
        default=None,
        description=(
            "Ensemble des mandats de l’acteur, décrivant chaque exercice de fonction au sein d’un organe (ex. groupe politique, commission, assemblée)."
        ) 
    )