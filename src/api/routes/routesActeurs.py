from fastapi import APIRouter, Query, status

from src.api.routes.acteurReponse import ActeurReponse
from src.metier.acteur.acteur import Acteur
from src.metier.acteur.enregistrerActeurs import mettre_a_jour_acteurs
from src.metier.acteur.recupererActeur import recuperer_acteur

router = APIRouter(prefix="/v1/acteurs", tags=["acteurs"])


@router.get(
    "/{uid}",
    response_model=ActeurReponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def retourne_acteur(
    uid: str,
    legislature: str | None = Query(
        default=None,
        description="Numéro de legislature (ex: '17').",
    ),
) -> ActeurReponse:
    acteur: Acteur = recuperer_acteur(uid, legislature=legislature)
    return ActeurReponse.model_validate(
        acteur.model_dump(mode="python", by_alias=True)
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def met_a_jour_acteurs():
    return mettre_a_jour_acteurs()