"""Organes API routes."""
from fastapi import APIRouter, status

from src.metier.organe.organe import Organe
from src.metier.organe.enregistrerOrgane import mettre_a_jour_organes
from src.metier.organe.recupererOrgane import recuperer_organe
from src.organeReponse import OrganeReponse

router = APIRouter(prefix="/v1/organes", tags=["organes"])


@router.get(
    "/{uid}",
    response_model=OrganeReponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def retrieve_organe(uid: str) -> OrganeReponse:
    """Retrieve an organe by UID."""
    organe: Organe = recuperer_organe(uid)
    return OrganeReponse.model_validate(
        organe.model_dump(mode="python", by_alias=True)
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def refresh_organes():
    """Trigger a refresh of the organes catalogue."""
    return mettre_a_jour_organes()
