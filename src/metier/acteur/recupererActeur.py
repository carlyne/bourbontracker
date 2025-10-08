import logging

from pydantic import ValidationError
from typing import Dict, List, Optional

from src.metier.organe.organe import Organe, parser_organe_depuis_payload
from src.infra.acteur.rechercherActeur import RechercherActeur
from src.metier.applicationExceptions import ActeurIntrouvableException
from src.metier.acteur.acteur import Acteur, Mandat, Mandats, parser_acteur_depuis_payload

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