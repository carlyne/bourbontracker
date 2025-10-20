from fastapi import APIRouter, Query, status

from src.api.schemas.acteurReponse import ActeurReponse
from src.metier.acteur.acteur import Acteur
from src.metier.acteur.enregistrerActeurs import créer_ou_raffraichir_données_acteurs
from src.metier.acteur.recupererActeur import recuperer_acteur

router = APIRouter(prefix="/v1/acteurs", tags=["acteurs"])


@router.get(
    "/{uid}",
    response_model=ActeurReponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Récupère un acteur par son identifiant",
    description=(
        "Récupère une entité « Acteur » identifiée par `uid`. "
        "Optionnellement, les paramètres `legislature` et `groupe_politique_uid` "
        "permettent de restreindre les mandats retournés."
    ),
    responses={
        200: {"description": "Acteur trouvé"},
        400: {"description": "Paramètre de requête invalide"},
        404: {"description": "Acteur non trouvé"},
        500: {"description": "Erreur interne serveur"}
    }
)
def retourne_acteur(
    uid: str,
    legislature: str | None = Query(
        default=None,
        description="Numéro de legislature facultatif (ex: '17').",
    ),
    groupe_politique_uid: str | None = Query(
        default=None,
        description="Identifiant d'un groupe politique (ex: 'PO123456').",
    ),
) -> ActeurReponse:
    acteur: Acteur = recuperer_acteur(
        uid,
        legislature=legislature,
        groupe_politique_uid=groupe_politique_uid,
    )

    return ActeurReponse.model_validate(
        acteur.model_dump(mode="python", by_alias=True)
    )


@router.post(
    "", 
    status_code=status.HTTP_201_CREATED,
    summary="Crée ou met à jour les données des acteurs",
    responses={
        201: {"description": "Traitement initié/réussi"},
        500: {"description": "Erreur interne serveur"}
    }
)
def crée_ou_raffraichis_données_acteurs():
    return créer_ou_raffraichir_données_acteurs()