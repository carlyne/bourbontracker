from fastapi import APIRouter, status

from src.metier.organe.organe import Organe
from src.metier.organe.enregistrerOrgane import créer_ou_raffraichir_données_organes
from src.metier.organe.recupererOrgane import recuperer_organe
from src.api.schemas.organeReponse import OrganeReponse

router = APIRouter(
    prefix="/v1/organes", 
    tags=["organes"]
)

@router.get(
    "/{uid}",
    response_model=OrganeReponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Récupère un organe par son identifiant",
    responses={
        200: {"description": "Organe trouvé"},
        404: {"description": "Organe non trouvé"},
        500: {"description": "Erreur interne serveur"}
    }
)
def retourne_organe(uid: str) -> OrganeReponse:
    organe: Organe = recuperer_organe(uid)
    
    return OrganeReponse.model_validate(
        organe.model_dump(mode="python", by_alias=True)
    )


@router.post(
    "", 
    status_code=status.HTTP_201_CREATED,
    summary="Crée ou met à jour les données des organes",
    responses={
        201: {"description": "Traitement initié/réussi"},
        500: {"description": "Erreur interne serveur"}
    }
)
def crée_ou_raffraichis_données_organes():
    return créer_ou_raffraichir_données_organes()