from fastapi import APIRouter, Query, status

from src.api.schemas.acteurReponse import ActeurReponse
from src.metier.acteur.acteur import Acteur
from src.metier.acteur.enregistrerActeurs import créer_ou_raffraichir_données_acteurs
from src.metier.acteur.recupererActeur import (
    recuperer_acteur, 
    recuperer_acteur_v2
)

router = APIRouter(prefix="/v1/acteurs", tags=["acteurs"])


@router.get(
    "/{uid}",
    response_model=ActeurReponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Récupère un acteur par son identifiant",
    description=(
        "Récupère une entité « Acteur » identifiée par `uid`. "
        "Optionnellement, le paramètre `legislature` permet de filtrer selon une législature donnée."
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
        description="Numéro de legislature facultatif (ex: '17')."
    ),
    type_organe: str | None = Query(
        default=None,
        description="Type d'organe auquel l'acteur appartient (ex: 'GP' pour 'Groupe Politique')."
    )
) -> ActeurReponse:
    acteur: Acteur = recuperer_acteur_v2(
        uid, 
        legislature, 
        type_organe
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