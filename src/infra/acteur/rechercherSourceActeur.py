from __future__ import annotations

import logging

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import (
    selectinload, 
    joinedload,
    with_loader_criteria
)

from src.infra.infrastructureException import LectureException
from src.infra.models import ActeurModel, MandatModel
from src.metier.acteur.acteur import Organes, Acteur
from src.metier.organe.organe import Organe
from src.infra.baseConnexionBdd import BaseConnexionBdd


logger = logging.getLogger(__name__)


class RechercherSourceActeur(BaseConnexionBdd):
    def __init__(self):
        super().__init__()

    def _construire_critères_de_recherche(self, legislature: Optional[str], type_organe: Optional[str]):
        logger.debug(
            "Construction des critères de recherche pour récupérer un acteur, ses mandats et organes pour la législature '%s' et le type d'ogane '%s'",
            legislature, type_organe
        )

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
                    lambda mandat: and_(*mandat_filtrés), 
                    include_aliases=True
                )
            )

        return options
    
    def _constuire_requête(self, uid: str, options):
        logger.debug(
            "Construction de la requête de récupération pour l'acteur '%s' et les critères de recherche : %s", 
            uid, options
        )

        return select(ActeurModel).where(ActeurModel.uid == uid).options(*options)
    
    def _executer_requête_en_base(self, requête) -> Optional[ActeurModel]:
        logger.debug(
            "Exécution de la requête : %s", 
            requête
        )

        with self.ouvrir_session() as session:
            return session.execute(requête).scalar_one_or_none()
        
    def _parser_en_objet_métier(self, acteur_model: ActeurModel) -> Acteur:
        logger.debug(
            "Mapping de l'acteur model : %s vers l'objet métier", 
            acteur_model
        )

        acteur = Acteur.model_validate(acteur_model, from_attributes=True)

        if acteur.mandats and acteur_model.mandats:
            for index, mandat_model in enumerate(acteur_model.mandats):
                if index >= len(acteur.mandats.mandat):
                    break

                mandat = acteur.mandats.mandat[index]

                mandat.organes = Organes(
                    organeRef=mandat_model.organe_uid,
                    detail=(Organe.model_validate(mandat_model.organe, from_attributes=True) if mandat_model.organe else None)
                )

        return acteur                                          
    

    def recherche_par_uid_et_critères(
            self,
            uid: str,
            legislature: Optional[str] = None,
            type_organe: Optional[str] = None

        ) -> Optional[Acteur]:
            logger.debug(
                "Recherche en base pour l'acteur '%s', la legislature '%s' et le type d'organe '%s'",
                uid, legislature, type_organe
            )

            try:
                critères_de_recherche = self._construire_critères_de_recherche(legislature, type_organe)
                requête = self._constuire_requête(uid, critères_de_recherche)
                
                acteur_model: ActeurModel = self._executer_requête_en_base(requête)

                if acteur_model is None:
                    logger.warning("Aucun uid '%s' présent en base pour cet acteur", uid)
                    return None
                
                return self._parser_en_objet_métier(acteur_model)
            
            except (Exception) as e:
                logger.exception("Erreur lors de la récupération des données pour l'acteur '%s'", uid)
                raise LectureException(f"Erreur lors de la récupération des données pour l'acteur '{uid}'") from e