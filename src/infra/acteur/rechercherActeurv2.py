from __future__ import annotations

import logging

from typing import (
    Optional, 
    List
)
from sqlalchemy import (
    select, 
    and_
)
from sqlalchemy.orm import (
    selectinload,
    joinedload,
    with_loader_criteria,
)

from src.infra.models import (
    ActeurModel, 
    MandatModel
)
from src.metier.acteur.acteur import (
    Acteur as ActeurMetier, 
    Organes, 
    Acteur
) 
from src.metier.organe.organe import Organe as OrganeMetier
from src.infra.baseConnexionBdd import BaseConnexionBdd


logger = logging.getLogger(__name__)


class RechercherActeurEnBaseV2(BaseConnexionBdd):
    def __init__(self):
        super().__init__()

    def recherche_par_uid(
        self,
        uid: str,
        legislature: Optional[str] = None,
        type_organe: Optional[str] = None,
) ->  Optional[Acteur]:
        mandat_filtrés: List = []

        if legislature:
            mandat_filtrés.append(MandatModel.legislature == legislature)
        if type_organe:
            mandat_filtrés.append(MandatModel.type_organe == type_organe)

        options = [
            selectinload(ActeurModel.mandats).options(
                joinedload(MandatModel.organe),                
                selectinload(MandatModel.collaborateurs),     
                selectinload(MandatModel.suppleants)        
            )
        ]

        if mandat_filtrés:
            options.append(
                with_loader_criteria(
                    MandatModel,
                    lambda cls: and_(*mandat_filtrés),
                    include_aliases=True,
                )
            )

        query = (
            select(ActeurModel)
            .where(ActeurModel.uid == uid)
            .options(*options)
        )

        with self.ouvrir_session() as session:
            acteur_model = session.execute(query).scalar_one_or_none()  
             
        if acteur_model is None:
            return None

        acteur_metier: ActeurMetier = ActeurMetier.model_validate(
            acteur_model, 
            from_attributes=True
        )

        if acteur_metier.mandats and acteur_model.mandats:
            organe_uid = {}
            for mandat in acteur_model.mandats:
                if mandat.organe and mandat.organe.uid not in organe_uid:
                    organe_uid[mandat.organe.uid] = OrganeMetier.model_validate(
                        mandat.organe, 
                        from_attributes=True
                    )

            for mandat_metier in acteur_metier.mandats.mandat:
                organe_ref = getattr(mandat_metier.organes, "organeRef", None)

                if organe_ref:
                    detail = organe_uid.get(organe_ref)
                    mandat_metier.organes = Organes(
                        organeRef=organe_ref, 
                        detail=detail
                    )

        return acteur_metier
