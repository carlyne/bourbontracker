import logging

from typing import Dict, List, Optional

from src.metier.organe.organe import Organe, parser_organe_depuis_payload
from src.infra.acteur.rechercherActeur import RechercherActeurEnBase
from src.metier.metierExceptions import DonnéeIntrouvableException, RecupererDonnéeException
from src.metier.acteur.acteur import (
    Acteur,
    Collaborateur,
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
    Suppleant,
    Suppleants,
    Uid,
)
from src.infra.models import (
    ActeurModel,
    MandatModel,
    OrganeModel,
)

TYPE_GROUPE_POLITIQUE: str = "GP"

logger = logging.getLogger(__name__)


def _filtrer_mandats_sur_groupe_politique(acteur: Acteur) -> List[Mandat]:
    return [mandat for mandat in acteur.mandats.mandat if mandat.typeOrgane == TYPE_GROUPE_POLITIQUE]

def _filtrer_mandats_par_legislature(
    mandats: List[Mandat],
    legislature: Optional[str]
) -> List[Mandat]:
    if legislature is None:
        return mandats
    return [mandat for mandat in mandats if mandat.legislature == legislature]

def _éditer_avec_mandats_filtrés(
    acteur: Acteur,
    mandats: List[Mandat]
) -> Acteur:
    return acteur.model_copy(update={"mandats": Mandats(mandat=mandats)})

def recuperer_acteur(
    uid: str,
    legislature: Optional[str] = None
) -> Acteur:
    rechercher_acteur_en_base = RechercherActeurEnBase()
    acteur_model, organes_model = rechercher_acteur_en_base.recherche_par_uid(uid)

    if acteur_model is None:
        raise DonnéeIntrouvableException(f"Acteur introuvable pour uid '{uid}'")

    try:
        acteur: Acteur = _parser_en_objet_metier(acteur_model, organes_model)
        mandats_filtrés_par_type: List[Mandat] = _filtrer_mandats_sur_groupe_politique(acteur)
        
        if not mandats_filtrés_par_type:
            logger.warning("Acteur %s sans mandat de type 'groupe politique'", uid)
            mandats_filtrés_par_type = acteur.mandats
        
        mandats_filtrés_par_legislature: List[Mandat] = _filtrer_mandats_par_legislature(mandats_filtrés_par_type, legislature)
        mandats_enrichis = _enrichir_mandats_avec_détail_des_organes(mandats_filtrés_par_legislature)
        acteur = _éditer_avec_mandats_filtrés(acteur, mandats_enrichis)

        return acteur

    except Exception as e:
        logger.error("Erreur validation acteur uid=%s : %s", uid, e)
        raise RecupererDonnéeException(f"Acteur invalide pour uid='{uid}'") from e

def _parser_en_objet_metier(
        acteur: ActeurModel,
        organes: List[OrganeModel],
) -> Acteur:
    organes_par_uid = {organe.uid: organe for organe in organes if organe.uid}

    etat_civil = _construire_etat_civil(acteur)
    profession = _construire_profession(acteur)

    mandats = [
        _convertir_mandat_en_modele_metier(mandat, organes_par_uid)
        for mandat in acteur.mandats
    ]

    return Acteur(
        uid=Uid(text=acteur.uid),
        etatCivil=etat_civil,
        profession=profession,
        url_fiche_acteur=acteur.url_fiche_acteur,
        mandats=Mandats(mandat=mandats),
    )


def _construire_etat_civil(acteur: ActeurModel) -> Optional[EtatCivil]:
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


def _construire_profession(acteur: ActeurModel) -> Optional[Profession]:
    soc_proc = SocProcINSEE(
        catSocPro=acteur.categorie_socio_professionnelle,
        famSocPro=acteur.famille_socio_professionnelle,
    )
    if not any((soc_proc.catSocPro, soc_proc.famSocPro)):
        soc_proc = None

    if acteur.profession_libelle is None and soc_proc is None:
        return None

    return Profession(libelleCourant=acteur.profession_libelle, socProcINSEE=soc_proc)


def _convertir_mandat_en_modele_metier(
        mandat: MandatModel,
        organes_par_uid: Dict[str, OrganeModel],
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
        Collaborateur(
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
        Suppleant(
            dateDebut=suppleant.date_debut,
            dateFin=suppleant.date_fin,
            suppleantRef=suppleant.suppleant_uid,
        )
        for suppleant in mandat.suppleants
    ]
    suppleants_modele = Suppleants(suppleant=suppleants) if suppleants else None

    organe_detail = None
    if mandat.organe_uid:
        organe = organes_par_uid.get(mandat.organe_uid)
        if organe is not None:
            organe_detail = Organe.model_validate(organe)

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