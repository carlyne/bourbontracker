from __future__ import annotations

import json
import logging
from typing import Iterable

from pydantic import ValidationError
from sqlalchemy.orm import Session as SASession

from src.infra._baseStockage import _BaseStockage
from src.infra.models import ActeurV2, Document, DocumentActeur, DocumentV2
from src.metier.document.document import (
    Acteur as DocumentActeurMetier,
    Auteur as AuteurMetier,
    Classification,
    Classe,
    Depot,
    Document as DocumentMetier,
    Espece,
    Famille,
    Notice,
    OrganesReferents,
    SousType,
    Titres,
    Type_,
    parse_document_depuis_payload,
)

logger = logging.getLogger(__name__)


def _nettoyer_chaine(valeur: str | None) -> str | None:
    if valeur is None:
        return None
    valeur_normalisee = valeur.strip()
    return valeur_normalisee or None


class MettreAJourStockDocuments(_BaseStockage):

    def __init__(self):
        super().__init__(
            nom_dossier_zip="dossier_legislatifs.zip",
            nom_dossier="document",
            url=(
                "http://data.assemblee-nationale.fr/static/openData/repository/17/loi/dossiers_legislatifs/"
                "Dossiers_Legislatifs.json.zip"
            ),
        )

        self._mettre_a_jour_stock_v2()

    def _mettre_a_jour_stock(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            try:
                total_documents = self._enregistrer_depuis_dossier(session, Document, batch_size=1000)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception(
                    "Rollback de la transaction en raison d'une erreur lors de la mise à jour des documents"
                )
                raise
        return total_documents

    def _mettre_a_jour_stock_v2(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            try:
                total_documents = self._enregistrer_documents_v2_depuis_dossier(session, batch_size=50)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception(
                    "Rollback de la transaction en raison d'une erreur lors de la mise à jour des documents V2"
                )
                raise
        return total_documents

    def _enregistrer_documents_v2_depuis_dossier(
        self, session: SASession, batch_size: int = 50
    ) -> int:
        compteur_total = 0
        batch: list[DocumentMetier] = []

        fichiers = self._itérer_dans_le_dossier_dezippé()
        if fichiers is None:
            logger.warning("Aucun fichier JSON trouvé pour les documents")
            return 0

        for fichier in fichiers:
            try:
                with fichier.open("r", encoding="utf-8") as contenu:
                    payload: dict = json.load(contenu)
            except (json.JSONDecodeError, OSError, ValueError):
                logger.exception("JSON illisible/invalide: %s", fichier)
                continue

            try:
                document = parse_document_depuis_payload(payload)
            except ValidationError as erreur:
                logger.warning("Document invalide ignoré (%s): %s", fichier.name, erreur)
                continue

            batch.append(document)

            if len(batch) >= batch_size:
                self._creer_ou_mettre_a_jour_documents_v2(session, batch)
                compteur_total += len(batch)
                batch.clear()

        if batch:
            self._creer_ou_mettre_a_jour_documents_v2(session, batch)
            compteur_total += len(batch)

        return compteur_total

    def _creer_ou_mettre_a_jour_documents_v2(
        self, session: SASession, documents: Iterable[DocumentMetier]
    ) -> None:
        for document in documents:
            self._creer_ou_mettre_a_jour_document_v2(session, document)

    def _creer_ou_mettre_a_jour_document_v2(
        self, session: SASession, document_metier: DocumentMetier
    ) -> None:
        uid = _nettoyer_chaine(document_metier.uid)
        if not uid:
            logger.warning("Document ignoré car UID manquant")
            return

        document_v2 = session.get(DocumentV2, uid)
        if document_v2 is None:
            document_v2 = DocumentV2(uid=uid)
            session.add(document_v2)

        document_v2.legislature = _nettoyer_chaine(document_metier.legislature)

        chrono = getattr(getattr(document_metier, "cycleDeVie", None), "chrono", None)
        document_v2.date_creation = getattr(chrono, "dateCreation", None)
        document_v2.date_depot = getattr(chrono, "dateDepot", None)
        document_v2.date_publication = getattr(chrono, "datePublication", None)
        document_v2.date_publication_web = getattr(chrono, "datePublicationWeb", None)

        titres: Titres | None = getattr(document_metier, "titres", None)
        document_v2.titre_principal = _nettoyer_chaine(getattr(titres, "titrePrincipal", None))
        document_v2.titre_principal_court = _nettoyer_chaine(getattr(titres, "titrePrincipalCourt", None))

        document_v2.denomination_structurelle = _nettoyer_chaine(
            getattr(document_metier, "denominationStructurelle", None)
        )
        document_v2.provenance = _nettoyer_chaine(getattr(document_metier, "provenance", None))
        document_v2.dossier_ref = _nettoyer_chaine(getattr(document_metier, "dossierRef", None))

        notice: Notice | None = getattr(document_metier, "notice", None)
        document_v2.notice_num_notice = _nettoyer_chaine(getattr(notice, "numNotice", None))
        document_v2.notice_formule = _nettoyer_chaine(getattr(notice, "formule", None))
        document_v2.notice_adoption_conforme = _nettoyer_chaine(
            getattr(notice, "adoptionConforme", None)
        )

        classification: Classification | None = getattr(document_metier, "classification", None)
        self._mettre_a_jour_classification(document_v2, classification)

        organes_referents = self._extraire_organes_referents(document_metier)
        document_v2.organes_referents = organes_referents

        redacteur = getattr(document_metier, "redacteur", None)
        if isinstance(redacteur, (dict, list)):
            document_v2.redacteur = redacteur
        else:
            document_v2.redacteur = None

        document_v2.auteurs.clear()
        for index, auteur in enumerate(self._extraire_auteurs(document_metier), start=1):
            document_acteur = self._convertir_auteur(session, auteur, index)
            if document_acteur is not None:
                document_v2.auteurs.append(document_acteur)

    def _mettre_a_jour_classification(
        self, document_v2: DocumentV2, classification: Classification | None
    ) -> None:
        if classification is None:
            document_v2.classification_famille_depot_code = None
            document_v2.classification_famille_depot_libelle = None
            document_v2.classification_famille_classe_code = None
            document_v2.classification_famille_classe_libelle = None
            document_v2.classification_famille_espece_code = None
            document_v2.classification_famille_espece_libelle = None
            document_v2.classification_famille_espece_libelle_edition = None
            document_v2.classification_type_code = None
            document_v2.classification_type_libelle = None
            document_v2.classification_sous_type_code = None
            document_v2.classification_sous_type_libelle = None
            document_v2.classification_sous_type_libelle_edition = None
            document_v2.classification_statut_adoption = None
            return

        famille: Famille | None = getattr(classification, "famille", None)
        depot: Depot | None = getattr(famille, "depot", None) if famille else None
        classe: Classe | None = getattr(famille, "classe", None) if famille else None
        espece: Espece | None = getattr(famille, "espece", None) if famille else None

        document_v2.classification_famille_depot_code = _nettoyer_chaine(getattr(depot, "code", None))
        document_v2.classification_famille_depot_libelle = _nettoyer_chaine(getattr(depot, "libelle", None))

        document_v2.classification_famille_classe_code = _nettoyer_chaine(getattr(classe, "code", None))
        document_v2.classification_famille_classe_libelle = _nettoyer_chaine(getattr(classe, "libelle", None))

        document_v2.classification_famille_espece_code = _nettoyer_chaine(getattr(espece, "code", None))
        document_v2.classification_famille_espece_libelle = _nettoyer_chaine(getattr(espece, "libelle", None))
        document_v2.classification_famille_espece_libelle_edition = _nettoyer_chaine(
            getattr(espece, "libelleEdition", None)
        )

        type_: Type_ | None = getattr(classification, "type_", None)
        document_v2.classification_type_code = _nettoyer_chaine(getattr(type_, "code", None))
        document_v2.classification_type_libelle = _nettoyer_chaine(getattr(type_, "libelle", None))

        sous_type: SousType | None = getattr(classification, "sousType", None)
        document_v2.classification_sous_type_code = _nettoyer_chaine(getattr(sous_type, "code", None))
        document_v2.classification_sous_type_libelle = _nettoyer_chaine(getattr(sous_type, "libelle", None))
        document_v2.classification_sous_type_libelle_edition = _nettoyer_chaine(
            getattr(sous_type, "libelleEdition", None)
        )

        document_v2.classification_statut_adoption = _nettoyer_chaine(
            getattr(classification, "statutAdoption", None)
        )

    def _extraire_auteurs(self, document: DocumentMetier) -> list[AuteurMetier]:
        auteurs = getattr(document, "auteurs", None)
        if not auteurs or not getattr(auteurs, "auteur", None):
            return []
        return list(auteurs.auteur)

    def _extraire_organes_referents(self, document: DocumentMetier) -> list[str]:
        organes: OrganesReferents | dict | None = getattr(document, "organesReferents", None)
        if not organes:
            return []

        organe_refs = getattr(organes, "organeRef", None)
        if isinstance(organes, dict):
            organe_refs = organes.get("organeRef")

        if isinstance(organe_refs, list):
            return [ref for ref in (_nettoyer_chaine(str(item)) for item in organe_refs) if ref]
        if isinstance(organe_refs, str):
            valeur = _nettoyer_chaine(organe_refs)
            return [valeur] if valeur else []

        return []

    def _convertir_auteur(
        self, session: SASession, auteur_metier: AuteurMetier, ordre: int
    ) -> DocumentActeur | None:
        acteur: DocumentActeurMetier | None = getattr(auteur_metier, "acteur", None)
        if acteur is None:
            return None

        acteur_ref = _nettoyer_chaine(getattr(acteur, "acteurRef", None))
        qualite = _nettoyer_chaine(getattr(acteur, "qualite", None))

        if acteur_ref is None and qualite is None:
            return None

        document_acteur = DocumentActeur(
            acteur_ref=acteur_ref,
            qualite=qualite,
            ordre=ordre,
        )

        if acteur_ref:
            acteur_v2 = session.get(ActeurV2, acteur_ref)
            if acteur_v2 is not None:
                document_acteur.acteur = acteur_v2

        return document_acteur