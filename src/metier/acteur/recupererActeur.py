import logging

from pydantic import ValidationError
from typing import Dict, List, Optional

from src.metier.organe.organe import Organe, parser_organe_depuis_payload
from src.infra.acteur.rechercherActeur import RechercherActeur
from src.metier.applicationExceptions import ActeurIntrouvableException
from src.metier.acteur.acteur import (
    Acteur,
    Collaborateur as CollaborateurModele,
    Collaborateurs,
    Election,
    EtatCivil,
    Ident,
    InfoNaissance,
    InfosQualite,
    Lieu,
    Mandat,
    Mandats,
    Mandature,
    Organes,
    Profession,
    SocProcINSEE,
    Suppleant as SuppleantModele,
    Suppleants,
    Uid,
    parser_acteur_depuis_payload,
)
from src.infra.models import (
    ActeurV2 as ActeurV2Model,
    Mandat as MandatModel,
    OrganeV2 as OrganeV2Model,
)

logger = logging.getLogger(__name__)

def recuperer_acteur(
        uid: str | None = None,
        legislature: Optional[str] = None
) -> Acteur:
    rechercher_acteur = RechercherActeur()

    acteur_payload, organes_payload = rechercher_acteur.recuperer_acteur_par_uid(uid)

    if not acteur_payload:
        raise ActeurIntrouvableException(f"Acteur introuvable pour uid='{uid}'")

    try:
        acteur: Acteur = parser_acteur_depuis_payload(acteur_payload)
        mandats = _extraire_mandats_type_groupe_politique(acteur)

        if not mandats:
            logger.warning("Acteur %s non représenté par un groupe politique", uid)
            raise ActeurIntrouvableException(
                f"l'Acteur avec uid='{uid}' n'est pas dans un groupe politique"
            )

        mandats = _filtrer_mandats_par_legislature(mandats, legislature)

        if not organes_payload:
            logger.warning("Aucun organe associé à l'acteur %s", uid)
            return _mettre_a_jour_mandats(acteur, mandats)

        mandats_enrichis = _enrichir_mandats_avec_détail_des_organes(mandats, organes_payload)

        return _mettre_a_jour_mandats(acteur, mandats_enrichis)

    except ValidationError as e:
        logger.error("Erreur de validation pour le fichier Acteur avec uid=%s : %s", uid, e)
        raise ActeurIntrouvableException(
            f"Acteur invalide dans le fichier: {uid}.json"
        ) from e
    
def recuperer_acteur_v2(
        uid: str | None = None,
        legislature: Optional[str] = None,
) -> Acteur:
    rechercher_acteur = RechercherActeur()

    acteur_v2, organes_v2 = rechercher_acteur.recuperer_acteur_par_uid_v2(uid)

    if acteur_v2 is None:
        raise ActeurIntrouvableException(f"Acteur introuvable pour uid='{uid}'")

    try:
        acteur: Acteur = _convertir_acteur_v2_en_modele_metier(acteur_v2, organes_v2)
        mandats = _extraire_mandats_type_groupe_politique(acteur)

        if not mandats:
            logger.warning("Acteur %s non représenté par un groupe politique", uid)
            raise ActeurIntrouvableException(
                f"l'Acteur avec uid='{uid}' n'est pas dans un groupe politique"
            )

        mandats = _filtrer_mandats_par_legislature(mandats, legislature)

        return _mettre_a_jour_mandats(acteur, mandats)

    except ValidationError as e:
        logger.error("Erreur de validation pour le fichier Acteur avec uid=%s : %s", uid, e)
        raise ActeurIntrouvableException(
            f"Acteur invalide dans le fichier: {uid}.json"
        ) from e

def _convertir_acteur_v2_en_modele_metier(
        acteur: ActeurV2Model,
        organes: List[OrganeV2Model],
) -> Acteur:
    organes_par_uid = {organe.uid: organe for organe in organes if organe.uid}

    etat_civil = _construire_etat_civil(acteur)
    profession = _construire_profession(acteur)

    mandats = [
        _convertir_mandat_v2_en_modele_metier(mandat, organes_par_uid)
        for mandat in acteur.mandats
    ]

    return Acteur(
        uid=Uid(text=acteur.uid),
        etatCivil=etat_civil,
        profession=profession,
        url_fiche_acteur=acteur.url_fiche_acteur,
        mandats=Mandats(mandat=mandats),
    )


def _construire_etat_civil(acteur: ActeurV2Model) -> Optional[EtatCivil]:
    ident = Ident(civ=acteur.civilite, prenom=acteur.prenom, nom=acteur.nom)
    if not any((ident.civ, ident.prenom, ident.nom)):
        ident = None

    info_naissance = InfoNaissance(
        dateNais=acteur.date_naissance,
        villeNais=acteur.ville_naissance,
        depNais=acteur.departement_naissance,
        paysNais=acteur.pays_naissance,
    )
    if not any((
        info_naissance.dateNais,
        info_naissance.villeNais,
        info_naissance.depNais,
        info_naissance.paysNais,
    )):
        info_naissance = None

    if ident is None and info_naissance is None:
        return None

    return EtatCivil(ident=ident, infoNaissance=info_naissance)


def _construire_profession(acteur: ActeurV2Model) -> Optional[Profession]:
    soc_proc = SocProcINSEE(
        catSocPro=acteur.categorie_socio_professionnelle,
        famSocPro=acteur.famille_socio_professionnelle,
    )
    if not any((soc_proc.catSocPro, soc_proc.famSocPro)):
        soc_proc = None

    if acteur.profession_libelle is None and soc_proc is None:
        return None

    return Profession(libelleCourant=acteur.profession_libelle, socProcINSEE=soc_proc)


def _convertir_mandat_v2_en_modele_metier(
        mandat: MandatModel,
        organes_par_uid: Dict[str, OrganeV2Model],
) -> Mandat:
    infos_qualite = None
    if any((mandat.infos_qualite_code, mandat.infos_qualite_libelle, mandat.infos_qualite_libelle_sexe)):
        infos_qualite = InfosQualite(
            codeQualite=mandat.infos_qualite_code,
            libQualite=mandat.infos_qualite_libelle,
            libQualiteSex=mandat.infos_qualite_libelle_sexe,
        )

    lieu = Lieu(
        region=mandat.lieu_region,
        regionType=mandat.lieu_region_type,
        departement=mandat.lieu_departement,
        numDepartement=mandat.lieu_num_departement,
        numCirco=mandat.lieu_num_circonscription,
    )
    if not any((
        lieu.region,
        lieu.regionType,
        lieu.departement,
        lieu.numDepartement,
        lieu.numCirco,
    )):
        lieu = None

    election = None
    if any((mandat.cause_mandat, mandat.ref_circonscription, lieu)):
        election = Election(
            causeMandat=mandat.cause_mandat,
            refCirconscription=mandat.ref_circonscription,
            lieu=lieu,
        )

    mandature = None
    if any((
        mandat.mandature_date_prise_fonction,
        mandat.mandature_cause_fin,
        mandat.mandature_premiere_election,
        mandat.mandature_place_hemicycle,
        mandat.mandature_mandat_remplace_ref,
    )):
        mandature = Mandature(
            datePriseFonction=mandat.mandature_date_prise_fonction,
            causeFin=mandat.mandature_cause_fin,
            premiereElection=mandat.mandature_premiere_election,
            placeHemicycle=mandat.mandature_place_hemicycle,
            mandatRemplaceRef=mandat.mandature_mandat_remplace_ref,
        )

    collaborateurs = [
        CollaborateurModele(
            qualite=collaborateur.qualite,
            prenom=collaborateur.prenom,
            nom=collaborateur.nom,
            dateDebut=collaborateur.date_debut,
            dateFin=collaborateur.date_fin,
        )
        for collaborateur in mandat.collaborateurs
    ]
    collaborateurs_modele = (
        Collaborateurs(collaborateur=collaborateurs)
        if collaborateurs
        else None
    )

    suppleants = [
        SuppleantModele(
            dateDebut=suppleant.date_debut,
            dateFin=suppleant.date_fin,
            suppleantRef=suppleant.suppleant_uid,
        )
        for suppleant in mandat.suppleants
    ]
    suppleants_modele = Suppleants(suppleant=suppleants) if suppleants else None

    organe_detail = None
    if mandat.organe_uid:
        organe_v2 = organes_par_uid.get(mandat.organe_uid)
        if organe_v2 is not None:
            organe_detail = Organe.model_validate(organe_v2)

    organes = None
    if mandat.organe_uid or organe_detail is not None:
        organes = Organes(organeRef=mandat.organe_uid, detail=organe_detail)

    return Mandat(
        uid=mandat.uid,
        acteurRef=mandat.acteur_uid,
        legislature=mandat.legislature,
        typeOrgane=mandat.type_organe,
        dateDebut=mandat.date_debut,
        datePublication=mandat.date_publication,
        dateFin=mandat.date_fin,
        preseance=mandat.preseance,
        nominPrincipale=mandat.nomin_principale,
        infosQualite=infos_qualite,
        organes=organes,
        suppleants=suppleants_modele,
        chambre=mandat.chambre,
        election=election,
        mandature=mandature,
        collaborateurs=collaborateurs_modele,
    )


def _extraire_mandats_type_groupe_politique(acteur: Acteur) -> List[Mandat]:
    mandats = acteur.mandats.mandat if (acteur.mandats and acteur.mandats.mandat) else []
    return [mandat for mandat in mandats if mandat.typeOrgane == "GP"]

def _filtrer_mandats_par_legislature(
        mandats: List[Mandat], 
        legislature: Optional[str]
) -> List[Mandat]:
    if not legislature:
        return mandats
    return [mandat for mandat in mandats if mandat.legislature == legislature]

def _enrichir_mandats_avec_détail_des_organes(
        mandats: List[Mandat], 
        organes_payload
) -> List[Mandat]:
    organes: List[Organe] = [parser_organe_depuis_payload(organe_payload) for organe_payload in organes_payload]
    organes_uids: Dict[str, Organe] = {organe.uid: organe for organe in organes if organe and organe.uid}
    mandats_enrichis: List[Mandat] = []
    
    for mandat in mandats:
        organe_ref = mandat.organes.organeRef if mandat.organes else None
        
        if organe_ref:
            detail = organes_uids.get(organe_ref)
            organes_avec_detail = mandat.organes.model_copy(update={"detail": detail})
            mandat = mandat.model_copy(update={"organes": organes_avec_detail})

        mandats_enrichis.append(mandat)
    
    return mandats_enrichis

def _mettre_a_jour_mandats(acteur: Acteur, mandats: List[Mandat]) -> Acteur:
    return acteur.model_copy(update={"mandats": Mandats(mandat=mandats)})