from __future__ import annotations

import logging

from typing import List, Optional
from sqlalchemy import select, or_, func, text
from sqlalchemy.orm import selectinload, joinedload

from src.metier.document.document import (
    Document,Titres, CycleDeVie, Chrono,Classification, Famille, Depot, Classe, Espece, Type_, 
    SousType,Auteurs, Auteur, Acteur as ActeurAuteurDom, OrganesReferents, Notice
)
from src.metier.acteur.acteur import Acteur, Mandat,Organe, Organes
from src.metier.organe.organe import Organe, ViMoDe
from src.infra.baseConnexionBdd import BaseConnexionBdd
from src.infra.infrastructureException import LectureException
from src.infra.models import DocumentModel, DocumentActeurModel, ActeurModel, MandatModel, OrganeModel


logger = logging.getLogger(__name__)


class RechercherSourceDocuments(BaseConnexionBdd):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _parser_vers_titres(document_model: DocumentModel) -> Optional[Titres]:
        if not (document_model.titre_principal or document_model.titre_principal_court):
            return None
        return Titres(titrePrincipal=document_model.titre_principal, titrePrincipalCourt=document_model.titre_principal_court)

    @staticmethod
    def _parser_vers_chrono(document_model: DocumentModel) -> Optional[CycleDeVie]:
        if not any([document_model.date_creation, document_model.date_depot, document_model.date_publication, document_model.date_publication_web]):
            return None
        return CycleDeVie(
            chrono=Chrono(
                dateCreation=document_model.date_creation,
                dateDepot=document_model.date_depot,
                datePublication=document_model.date_publication,
                datePublicationWeb=document_model.date_publication_web,
            )
        )

    @staticmethod
    def _parser_vers_classification(document_model: DocumentModel) -> Optional[Classification]:
        has_famille = any([
            document_model.classification_famille_depot_code,
            document_model.classification_famille_depot_libelle,
            document_model.classification_famille_classe_code,
            document_model.classification_famille_classe_libelle,
            document_model.classification_famille_espece_code,
            document_model.classification_famille_espece_libelle,
            document_model.classification_famille_espece_libelle_edition,
        ])
        has_type = any([document_model.classification_type_code, document_model.classification_type_libelle])
        has_soustype = any([
            document_model.classification_sous_type_code,
            document_model.classification_sous_type_libelle,
            document_model.classification_sous_type_libelle_edition,
        ])
        has_statut = document_model.classification_statut_adoption is not None

        if not any([has_famille, has_type, has_soustype, has_statut]):
            return None

        famille = Famille(
            depot=Depot(
                code=document_model.classification_famille_depot_code,
                libelle=document_model.classification_famille_depot_libelle,
            ) if (document_model.classification_famille_depot_code or document_model.classification_famille_depot_libelle) else None,
            classe=Classe(
                code=document_model.classification_famille_classe_code,
                libelle=document_model.classification_famille_classe_libelle,
            ) if (document_model.classification_famille_classe_code or document_model.classification_famille_classe_libelle) else None,
            espece=Espece(
                code=document_model.classification_famille_espece_code,
                libelle=document_model.classification_famille_espece_libelle,
                libelleEdition=document_model.classification_famille_espece_libelle_edition,
            ) if (document_model.classification_famille_espece_code or document_model.classification_famille_espece_libelle or document_model.classification_famille_espece_libelle_edition) else None,
        ) if has_famille else None

        type_ = Type_(
            code=document_model.classification_type_code,
            libelle=document_model.classification_type_libelle,
        ) if has_type else None

        sous_type = SousType(
            code=document_model.classification_sous_type_code,
            libelle=document_model.classification_sous_type_libelle,
            libelleEdition=document_model.classification_sous_type_libelle_edition,
        ) if has_soustype else None

        return Classification(
            famille=famille,
            type=type_,
            sousType=sous_type,
            statutAdoption=document_model.classification_statut_adoption,
        )

    @staticmethod
    def _parser_vers_vi_mo_de(organe_model: OrganeModel) -> Optional[ViMoDe]:
        if not any([organe_model.vimode_date_debut, organe_model.vimode_date_agrement, organe_model.vimode_date_fin]):
            return None
        
        return ViMoDe(
            dateDebut=organe_model.vimode_date_debut,
            dateAgrement=organe_model.vimode_date_agrement,
            dateFin=organe_model.vimode_date_fin,
        )

    def _parser_vers_organe(self, organe_model: Optional[OrganeModel]) -> Optional[Organe]:
        if organe_model is None:
            return None
        
        return Organe.model_validate(
            {
                "uid": organe_model.uid,
                "codeType": organe_model.code_type,
                "libelle": organe_model.libelle,
                "libelleEdition": organe_model.libelle_edition,
                "libelleAbrege": organe_model.libelle_abrege,
                "libelleAbrev": organe_model.libelle_abrev,
                "viMoDe": (self._parser_vers_vi_mo_de(organe_model).model_dump(by_alias=True) if self._parser_vers_vi_mo_de(organe_model) else None),
                "organeParent": organe_model.organe_parent,
                "preseance": organe_model.preseance,
                "organePrecedentRef": organe_model.organe_precedent_ref,
            }
        )

    def _enrichir_acteur_detail(self, acteur_model: ActeurModel, acteur: Acteur) -> None:
        if not (acteur.mandats and acteur_model.mandats):
            return

        def clé_metier(mandat: Mandat):
            return (
                (mandat.uid or ""),
                mandat.dateDebut,
                mandat.typeOrgane,
                getattr(mandat, "acteurRef", None)
            )

        def clé_model(mandat_model: MandatModel):
            return (
                (mandat_model.uid or ""),
                mandat_model.date_debut,
                mandat_model.type_organe,
                mandat_model.acteur_uid
            )

        par_cle = {clé_metier(mandat): mandat for mandat in (acteur.mandats.mandat or [])}

        for mandat_model in (acteur_model.mandats or []):
            mandat = par_cle.get(clé_model(mandat_model))
            if not mandat:
                continue
            mandat.organes = Organes(
                organeRef=mandat_model.organe_uid,
                detail=self._parser_vers_organe(mandat_model.organe)
            )

    def _parser_vers_auteurs(self, documents_acteurs_model: List[DocumentActeurModel]) -> Optional[Auteurs]:
        if not documents_acteurs_model:
            return None

        auteurs: List[Auteur] = []
        for auteur in documents_acteurs_model:
            acteur_ref = auteur.acteur_ref or (auteur.acteur.uid if auteur.acteur else None)
            acteur_detail = None
            if auteur.acteur is not None:
                acteur_detail = Acteur.model_validate(auteur.acteur, from_attributes=True)
                self._enrichir_acteur_detail(auteur.acteur, acteur_detail)

            auteurs.append(
                Auteur(
                    acteur=ActeurAuteurDom(
                        acteurRef=acteur_ref,
                        acteur_detail=acteur_detail,
                        qualite=auteur.qualite,
                    )
                )
            )

        return Auteurs(auteur=auteurs)

    def _parser_vers_document(self, document_model: DocumentModel) -> Document:
        auteurs = self._parser_vers_auteurs(document_model.auteurs)

        return Document.model_validate(
            {
                "uid": document_model.uid,
                "legislature": document_model.legislature,
                "cycleDeVie": (self._parser_vers_chrono(document_model).model_dump(by_alias=True)
                               if self._parser_vers_chrono(document_model) else None),
                "denominationStructurelle": document_model.denomination_structurelle,
                "provenance": document_model.provenance,
                "titres": (self._parser_vers_titres(document_model).model_dump(by_alias=True)
                           if self._parser_vers_titres(document_model) else None),
                "divisions": None,
                "dossierRef": document_model.dossier_ref,
                "redacteur": document_model.redacteur,
                "classification": (self._parser_vers_classification(document_model).model_dump(by_alias=True)
                                   if self._parser_vers_classification(document_model) else None),
                "auteurs": (auteurs.model_dump(by_alias=True) if auteurs else None),
                "correction": None,
                "notice": Notice(
                    numNotice=document_model.notice_num_notice,
                    formule=document_model.notice_formule,
                    adoptionConforme=document_model.notice_adoption_conforme,
                ).model_dump(by_alias=True) if any([document_model.notice_num_notice, document_model.notice_formule, document_model.notice_adoption_conforme]) else None,
                "indexation": None,
                "organesReferents": (OrganesReferents(organeRef=document_model.organes_referents).model_dump(by_alias=True)
                                     if document_model.organes_referents else None),
            },
            from_attributes=False
        )

    def _options_recherche_auteurs(self):
        return [
            selectinload(DocumentModel.auteurs).options(
                joinedload(DocumentActeurModel.acteur).options(
                    selectinload(ActeurModel.mandats).options(
                        joinedload(MandatModel.organe),
                        selectinload(MandatModel.collaborateurs),
                        selectinload(MandatModel.suppleants)
                    )
                )
            )
        ]


    def recherche_sur_semaine_courante(self) -> List[Document]:
        date_du_jour = func.current_date()
        six_jours_plus_tôt = func.current_date() - text("INTERVAL '6 days'")

        logger.debug(
            "Requête documents de la semaine courante. Date du jour : '%s'. 6 jours plus tôt : '%s'",
            date_du_jour, six_jours_plus_tôt
        )

        filtrage_par_date = or_(
            func.date(DocumentModel.date_creation).between(six_jours_plus_tôt, date_du_jour),
            func.date(DocumentModel.date_depot).between(six_jours_plus_tôt, date_du_jour),
            func.date(DocumentModel.date_publication).between(six_jours_plus_tôt, date_du_jour),
            func.date(DocumentModel.date_publication_web).between(six_jours_plus_tôt, date_du_jour),
        )

        requête = (
            select(DocumentModel)
            .where(filtrage_par_date)
            .options(*self._options_recherche_auteurs())
            .order_by(DocumentModel.date_publication.desc().nullslast())
        )

        try:
            with self.ouvrir_session() as session:
                documents_models: List[DocumentModel] = (
                    session.execute(requête).scalars().unique().all()
                )

            return [self._parser_vers_document(document_model) for document_model in documents_models]

        except Exception as e:
            logger.exception("Erreur inattendue lors de la lecture des documents: %s", e)
            raise LectureException("Erreur lors de la lecture des documents") from e
        
    def recherche_par_type_organe(self, type_organe: str) -> List[Document]:
        logger.debug("Requête documents par type d'organe : '%s'", type_organe)

        requête = (
            select(DocumentModel)
            .join(
                OrganeModel,
                DocumentModel.organes_referents.any(OrganeModel.uid)
            )
            .where(OrganeModel.code_type == type_organe)
            .options(*self._options_recherche_auteurs())
            .order_by(DocumentModel.date_publication.desc().nullslast())
        )

        try:
            with self.ouvrir_session() as session:
                documents_models: List[DocumentModel] = (
                    session.execute(requête).scalars().unique().all()
                )

            return [self._parser_vers_document(document_model) for document_model in documents_models]

        except Exception as e:
            logger.exception(
                "Erreur inattendue lors de la lecture des documents pour le type d'organe %s: %s",
                type_organe,
                e
            )
            raise LectureException("Erreur lors de la lecture des documents par type d'organe") from e