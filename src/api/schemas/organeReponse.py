from __future__ import annotations

from typing import Optional
from pydantic import (
    BaseModel, 
    ConfigDict, 
    Field
)

class OrganeReponse(BaseModel):
    """
    Documentation officielle des champs : https://www.assemblee-nationale.fr/opendata/Schemas_Entites/AMO/Schemas_Organes.html
    """

    model_config = ConfigDict(
        populate_by_name=True,
        # ignore les champs supplémentaires lors des parsing 
        extra="ignore"
    )

    uid: str = Field(
        # indique que le champ ne peut pas être nul
        ...,
        description="Identifiant unique de l’organe"
    )

    code_type: Optional[str] = Field(
        default=None,
        description="""
            Code du type d'organe.
            - GP : Groupe Politique
            - ORGEXTPARL : Organisme extra parlementaire
            - ASSEMBLEE : Assemblée nationale
            - CNPE : Commissions d’enquêtes
            - ect...
        """,
        alias="codeType",
    )

    libelle: Optional[str] = Field(
        default=None,
        description="Libellé (partiel ?) de l’organe. Ex : « Bretagne » pour le conseil régional de Bretagne"
    )