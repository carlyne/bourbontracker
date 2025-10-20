from __future__ import annotations

import json
import logging
from typing import Iterable

from pydantic import ValidationError
from sqlalchemy.orm import Session as SASession

from src.infra.models import (
    ActeurModel,
    CollaborateurModel,
    MandatModel,
    SuppleantModel,
)
from src.infra._baseStockage import _BaseStockage
from src.metier.acteur.acteur import (
    Acteur,
    Collaborateur,
    Mandat,
    Suppleant,
    parser_acteur_depuis_payload,
)

logger = logging.getLogger(__name__)

def _nettoyer_chaine(valeur: str | None) -> str | None:
    if valeur is None:
        return None
    valeur_normalisee = valeur.strip()
    return valeur_normalisee or None

class MettreAJourStockActeurs(_BaseStockage):
    def __init__(self):
        super().__init__(
            nom_dossier_zip="acteurs.zip",
            nom_dossier="acteur",
            url= (
                "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
                "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
            )
        )

        self._mettre_a_jour_stock()

    def _mettre_a_jour_stock(self) -> int:
        self._mettre_a_jour()
        with self.ouvrir_session() as session:
            try:
                total_acteurs = self._enregistrer_acteurs_depuis_dossier(session, batch_size=50)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception(
                    "Rollback de la transaction en raison d'une erreur lors de la mise à jour des acteurs"
                )
                raise
        return total_acteurs

    def _enregistrer_acteurs_depuis_dossier(
        self, session: SASession, batch_size: int = 50
    ) -> int:
        compteur_total = 0
        batch: list[Acteur] = []

        fichiers = self._itérer_dans_le_dossier_dezippé()
        if fichiers is None:
            logger.warning("Aucun fichier JSON trouvé pour les acteurs")
            return 0

        for fichier in fichiers:
            try:
                with fichier.open("r", encoding="utf-8") as contenu:
                    payload: dict = json.load(contenu)
            except (json.JSONDecodeError, OSError, ValueError):
                logger.exception("JSON illisible/invalide: %s", fichier)
                continue

            try:
                acteur = parser_acteur_depuis_payload(payload)
            except ValidationError as erreur:
                logger.warning("Acteur invalide ignoré (%s): %s", fichier.name, erreur)
                continue

            batch.append(acteur)

            if len(batch) >= batch_size:
                self._creer_ou_mettre_a_jour_acteurs(session, batch)
                compteur_total += len(batch)
                batch.clear()

        if batch:
            self._creer_ou_mettre_a_jour_acteurs(session, batch)
            compteur_total += len(batch)

        return compteur_total

    def _creer_ou_mettre_a_jour_acteurs(
        self, session: SASession, acteurs: Iterable[Acteur]
    ) -> None:
        for acteur in acteurs:
            self._creer_ou_mettre_a_jour_acteur(session, acteur)

    def _creer_ou_mettre_a_jour_acteur(
        self, session: SASession, acteur_metier: Acteur
    ) -> None:
        uid = _nettoyer_chaine(getattr(acteur_metier.uid, "text", None))
        if not uid:
            logger.warning("Acteur ignoré car UID manquant")
            return

        acteur = session.get(ActeurModel, uid)
        if acteur is None:
            acteur = ActeurModel(uid=uid)
            session.add(acteur)

        etat_civil = acteur_metier.etatCivil
        identite = getattr(etat_civil, "ident", None) if etat_civil else None
        info_naissance = getattr(etat_civil, "infoNaissance", None) if etat_civil else None

        acteur.civilite = _nettoyer_chaine(getattr(identite, "civ", None))
        acteur.prenom = _nettoyer_chaine(getattr(identite, "prenom", None))
        acteur.nom = _nettoyer_chaine(getattr(identite, "nom", None))
        acteur.date_naissance = getattr(info_naissance, "dateNais", None)
        acteur.ville_naissance = _nettoyer_chaine(getattr(info_naissance, "villeNais", None))
        acteur.departement_naissance = _nettoyer_chaine(
            getattr(info_naissance, "depNais", None)
        )
        acteur.pays_naissance = _nettoyer_chaine(getattr(info_naissance, "paysNais", None))
        acteur.date_deces = None

        profession = acteur_metier.profession
        acteur.profession_libelle = _nettoyer_chaine(
            getattr(profession, "libelleCourant", None)
        )
        soc_proc = getattr(profession, "socProcINSEE", None) if profession else None
        acteur.categorie_socio_professionnelle = _nettoyer_chaine(
            getattr(soc_proc, "catSocPro", None)
        )
        acteur.famille_socio_professionnelle = _nettoyer_chaine(
            getattr(soc_proc, "famSocPro", None)
        )
        acteur.url_fiche_acteur = _nettoyer_chaine(
            str(acteur_metier.url_fiche_acteur) if acteur_metier.url_fiche_acteur else None
        )

        # Les mandats existants doivent être remplacés pour garantir la synchronisation complète
        acteur.mandats.clear()
        for mandat in self._convertir_mandats(uid, acteur_metier.mandats.mandat if acteur_metier.mandats else []):
            acteur.mandats.append(mandat)

    def _convertir_mandats(
        self, acteur_uid: str, mandats_metier: Iterable[Mandat]
    ) -> Iterable[MandatModel]:
        mandats: list[MandatModel] = []
        for mandat_metier in mandats_metier:
            mandat = MandatModel(
                uid=_nettoyer_chaine(mandat_metier.uid),
                acteur_uid=acteur_uid,
                organe_uid=_nettoyer_chaine(
                    mandat_metier.organes.organeRef if mandat_metier.organes else None
                ),
                legislature=_nettoyer_chaine(mandat_metier.legislature),
                type_organe=_nettoyer_chaine(mandat_metier.typeOrgane),
                date_debut=mandat_metier.dateDebut,
                date_publication=mandat_metier.datePublication,
                date_fin=mandat_metier.dateFin,
                preseance=_nettoyer_chaine(mandat_metier.preseance),
                nomin_principale=_nettoyer_chaine(mandat_metier.nominPrincipale),
                infos_qualite_code=_nettoyer_chaine(
                    mandat_metier.infosQualite.codeQualite if mandat_metier.infosQualite else None
                ),
                infos_qualite_libelle=_nettoyer_chaine(
                    mandat_metier.infosQualite.libQualite if mandat_metier.infosQualite else None
                ),
                infos_qualite_libelle_sexe=_nettoyer_chaine(
                    mandat_metier.infosQualite.libQualiteSex if mandat_metier.infosQualite else None
                ),
                chambre=_nettoyer_chaine(mandat_metier.chambre),
                cause_mandat=_nettoyer_chaine(
                    mandat_metier.election.causeMandat if mandat_metier.election else None
                ),
                ref_circonscription=_nettoyer_chaine(
                    mandat_metier.election.refCirconscription if mandat_metier.election else None
                ),
                lieu_region=_nettoyer_chaine(
                    mandat_metier.election.lieu.region
                    if mandat_metier.election and mandat_metier.election.lieu
                    else None
                ),
                lieu_region_type=_nettoyer_chaine(
                    mandat_metier.election.lieu.regionType
                    if mandat_metier.election and mandat_metier.election.lieu
                    else None
                ),
                lieu_departement=_nettoyer_chaine(
                    mandat_metier.election.lieu.departement
                    if mandat_metier.election and mandat_metier.election.lieu
                    else None
                ),
                lieu_num_departement=_nettoyer_chaine(
                    mandat_metier.election.lieu.numDepartement
                    if mandat_metier.election and mandat_metier.election.lieu
                    else None
                ),
                lieu_num_circonscription=_nettoyer_chaine(
                    mandat_metier.election.lieu.numCirco
                    if mandat_metier.election and mandat_metier.election.lieu
                    else None
                ),
                mandature_date_prise_fonction=(
                    mandat_metier.mandature.datePriseFonction if mandat_metier.mandature else None
                ),
                mandature_cause_fin=_nettoyer_chaine(
                    mandat_metier.mandature.causeFin if mandat_metier.mandature else None
                ),
                mandature_premiere_election=_nettoyer_chaine(
                    mandat_metier.mandature.premiereElection if mandat_metier.mandature else None
                ),
                mandature_place_hemicycle=_nettoyer_chaine(
                    mandat_metier.mandature.placeHemicycle if mandat_metier.mandature else None
                ),
                mandature_mandat_remplace_ref=_nettoyer_chaine(
                    mandat_metier.mandature.mandatRemplaceRef if mandat_metier.mandature else None
                ),
            )

            collaborateurs = mandat_metier.collaborateurs.collaborateur if mandat_metier.collaborateurs else []
            suppleants = mandat_metier.suppleants.suppleant if mandat_metier.suppleants else []

            mandat.collaborateurs.extend(self._convertir_collaborateurs(collaborateurs))
            mandat.suppleants.extend(self._convertir_suppleants(suppleants))

            mandats.append(mandat)

        return mandats

    def _convertir_collaborateurs(
        self, collaborateurs: Iterable[Collaborateur]
    ) -> list[CollaborateurModel]:
        collaborateurs: list[CollaborateurModel] = []
        for collaborateur in collaborateurs:
            collaborateurs.append(
                CollaborateurModel(
                    qualite=_nettoyer_chaine(collaborateur.qualite),
                    prenom=_nettoyer_chaine(collaborateur.prenom),
                    nom=_nettoyer_chaine(collaborateur.nom),
                    date_debut=collaborateur.dateDebut,
                    date_fin=collaborateur.dateFin,
                )
            )
        return collaborateurs

    def _convertir_suppleants(
        self, suppleants: Iterable[Suppleant]
    ) -> list[SuppleantModel]:
        suppleants: list[SuppleantModel] = []
        for suppleant in suppleants:
            suppleants.append(
                SuppleantModel(
                    date_debut=suppleant.dateDebut,
                    date_fin=suppleant.dateFin,
                    suppleant_uid=_nettoyer_chaine(suppleant.suppleantRef),
                )
            )
        return suppleants
