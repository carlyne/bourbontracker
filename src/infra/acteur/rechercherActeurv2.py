from __future__ import annotations

import logging
from typing import Optional, List
from itertools import zip_longest

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload, with_loader_criteria, Session

from src.infra.models import ActeurModel, MandatModel
from src.metier.acteur.acteur import Acteur as ActeurMetier, Organes, Acteur
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
    ) -> Optional[Acteur]:
        """
        Récupère un Acteur + mandats filtrés (le cas échéant) et enrichit chaque mandat
        avec organes = { organeRef, detail = OrganeMetier }.

        Retourne None si l'acteur n'existe pas.
        """
        # 1) Prépare les filtres relationnels (appliqués globalement aux chargements de MandatModel)
        mandat_filtres: List = []
        if legislature:
            mandat_filtres.append(MandatModel.legislature == legislature)
        if type_organe:
            mandat_filtres.append(MandatModel.type_organe == type_organe)

        # 2) Eager-loading anti-N+1 :
        #    - collections -> selectinload
        #    - many-to-one léger -> joinedload
        options = [
            selectinload(ActeurModel.mandats).options(
                joinedload(MandatModel.organe),
                selectinload(MandatModel.collaborateurs),
                selectinload(MandatModel.suppleants),
            )
        ]
        if mandat_filtres:
            options.append(
                with_loader_criteria(
                    MandatModel,
                    lambda cls: and_(*mandat_filtres),
                    include_aliases=True,
                )
            )

        # 3) Requête principale (un seul aller-retour)
        stmt = (
            select(ActeurModel)
            .where(ActeurModel.uid == uid)
            .options(*options)
        )

        with self.ouvrir_session() as session:  
            acteur_model = session.execute(stmt).scalar_one_or_none()

        if acteur_model is None:
            return None

        # 4) Mapping ORM -> DTO Pydantic v2 depuis les attributs
        acteur_metier: ActeurMetier = ActeurMetier.model_validate(
            acteur_model, from_attributes=True
        )

        # 5) Enrichissement organes = { organeRef, detail }
        # NOTE : zip_longest suppose que l'ordre de la liste ORM et celui du DTO
        #        correspondent. Pour garantir un ordre stable, tu peux :
        #        - configurer relationship(order_by=MandatModel.id) côté ORM, ou
        #        - trier explicitement acteur_model.mandats avant la boucle.
        if acteur_metier.mandats and acteur_model.mandats:
            for m_orm, m_dto in zip_longest(
                acteur_model.mandats, acteur_metier.mandats.mandat, fillvalue=None
            ):
                if m_orm is None or m_dto is None:
                    continue
                org_ref = m_orm.organe_uid
                detail = (
                    OrganeMetier.model_validate(m_orm.organe, from_attributes=True)
                    if m_orm.organe else None
                )
                m_dto.organes = Organes(organeRef=org_ref, detail=detail)

        return acteur_metier