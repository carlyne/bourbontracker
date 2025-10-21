import logging

from typing import (
    Dict, 
    List, 
    Optional
)

from src.metier.organe.organe import Organe
from src.infra.acteur.rechercherActeur import RechercherActeurEnBase
from src.infra.acteur.rechercherActeurv2 import RechercherActeurEnBaseV2
from src.metier.metierExceptions import (
    DonnéeIntrouvableException, 
    RecupererDonnéeException
)
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
    Uid
)
from src.infra.models import (
    ActeurModel,
    MandatModel,
    OrganeModel
)

logger = logging.getLogger(__name__)


def _construire_etat_civil(acteur_model: ActeurModel) -> Optional[EtatCivil]:
    ident = Ident(civ=acteur_model.civilite, prenom=acteur_model.prenom, nom=acteur_model.nom)
    if not any((ident.civ, ident.prenom, ident.nom)):
        ident = None

    info_naissance = InfoNaissance(
        dateNais=acteur_model.date_naissance,
        villeNais=acteur_model.ville_naissance,
        depNais=acteur_model.departement_naissance,
        paysNais=acteur_model.pays_naissance,
    )
    if not any((info_naissance.dateNais, info_naissance.villeNais, info_naissance.depNais, info_naissance.paysNais)):
        info_naissance = None

    if ident is None and info_naissance is None:
        return None

    try:
        return EtatCivil.model_validate({"ident": ident, "infoNaissance": info_naissance})
    except Exception as e:
        logger.error("Erreur validation EtatCivil pour acteur %s : %s", acteur_model.uid, e)
        return None


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

    if not organes_par_uid is None:
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

def _parser_en_objet_metier(
        acteur: ActeurModel,
        organes: List[OrganeModel],
) -> Acteur:
    etat_civil = _construire_etat_civil(acteur)
    profession = _construire_profession(acteur)

    if organes is None:
        organes_par_uid = None
    else:
        organes_par_uid = {organe.uid: organe for organe in organes if organe.uid}

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

def _enrichir_mandats_avec_detail_organe(
    mandats: List[Mandat],
    organes_models: List[OrganeModel]
) -> List[Mandat]:
    
    organes_map = {organe_model.uid: Organe.model_validate(organe_model, from_attributes=True) for organe_model in organes_models if organe_model.uid}
    mandats_enrichis: List[Mandat] = []

    for mandat in mandats:
        if mandat.organes and mandat.organes.organeRef:
            detail = organes_map.get(mandat.organes.organeRef)
            if detail:
                mandat = mandat.model_copy(update={"organes": mandat.organes.model_copy(update={"detail": detail})})
        mandats_enrichis.append(mandat)

    return mandats_enrichis

def _filtrer_mandats(
    mandats: List[Mandat],
    legislature: Optional[str],
    type_organe: Optional[str]
) -> List[Mandat]:
    mandats_filtrés: List[Mandat] = mandats

    if type_organe is not None and legislature is not None:
        mandats_filtrés = [mandat for mandat in mandats_filtrés if mandat.typeOrgane == type_organe and mandat.legislature == legislature]
        if not mandats_filtrés:
           logger.warning("Aucun mandat trouvé pour le type d’organe '%s' et la législature '%s'", type_organe, legislature)
           return mandats_filtrés
        return mandats_filtrés 

    if type_organe is not None:
        mandats_filtrés = [mandat for mandat in mandats_filtrés if mandat.typeOrgane == type_organe]
        if not mandats_filtrés:
           logger.warning("Aucun mandat trouvé pour le type d’organe '%s'", type_organe)
           return mandats_filtrés
        return mandats_filtrés

    if legislature is not None:
        mandats_filtrés = [mandat for mandat in mandats_filtrés if mandat.legislature == legislature]

        if not mandats_filtrés:
            logger.warning("Aucun mandat trouvé pour la législature '%s'", legislature)
        return mandats_filtrés

def recuperer_acteur(
    uid: str,
    legislature: Optional[str] = None,
    type_organe: Optional[str] = None
) -> Acteur:
    repository = RechercherActeurEnBase()
    acteur_model, organes_model = repository.recherche_par_uid(uid)

    if acteur_model is None:
        raise DonnéeIntrouvableException(f"Acteur introuvable pour uid='{uid}'")

    try:
        acteur: Acteur = Acteur.model_validate(acteur_model, from_attributes=True)

        mandats_initials: List[Mandat] = acteur.mandats.mandat if acteur.mandats else []

        mandats_filtrés = _filtrer_mandats(
            mandats=mandats_initials,
            legislature=legislature,
            type_organe=type_organe
        )

        mandats_enrichis = _enrichir_mandats_avec_detail_organe(
            mandats=mandats_filtrés,
            organes_models=organes_model
        )

        acteur = acteur.model_copy(update={"mandats": Mandats(mandat=mandats_enrichis)})

        return acteur

    except Exception as e:
        logger.error("Erreur de validation pour l’acteur uid '%s'. Cause :  %s", uid, e)
        raise RecupererDonnéeException(f"Acteur invalide pour uid '{uid}'") from e
    
def recuperer_acteur_v2(
    uid: str,
    legislature: Optional[str] = None,
    type_organe: Optional[str] = None
):
    try:
        repository = RechercherActeurEnBaseV2()
        acteur = repository.recherche_par_uid(uid, legislature, type_organe)

        if acteur is None:
            raise DonnéeIntrouvableException(f"Acteur introuvable pour uid='{uid}'")
        return acteur
    except Exception as e:
        logger.error("Erreur de validation pour l’acteur uid '%s'. Cause :  %s", uid, e)
        raise RecupererDonnéeException(f"Acteur invalide pour uid '{uid}'") from e

