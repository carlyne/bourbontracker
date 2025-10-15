from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


def nil_ou_text(champ: Any) -> Optional[str]:
    if champ is None:
        return None
    if isinstance(champ, list):
        for element in champ:
            valeur = nil_ou_text(element)
            if valeur is not None:
                return valeur
        return None
    if isinstance(champ, str):
        champ_normalisé = champ.strip()
        return champ_normalisé or None
    if isinstance(champ, dict):
        if str(champ.get("@xsi:nil", "")).lower() == "true":
            return None
        for clé in ("#text", "text", "value"):
            valeur = champ.get(clé)
            if isinstance(valeur, str):
                valeur_normalisée = valeur.strip()
                if valeur_normalisée:
                    return valeur_normalisée
    return None


def transformer_en_liste(champ: Any) -> List[Any]:
    if champ is None:
        return []
    if isinstance(champ, (list, tuple)):
        return list(champ)
    return [champ]


def date_ou_none(champ: Any) -> Optional[date]:
    if champ is None:
        return None
    if isinstance(champ, list):
        for element in champ:
            valeur = date_ou_none(element)
            if valeur is not None:
                return valeur
        return None
    if isinstance(champ, dict):
        if str(champ.get("@xsi:nil", "")).lower() == "true":
            return None
        for clé in ("#text", "text", "value"):
            valeur = champ.get(clé)
            if valeur is not None:
                champ = valeur
                break
        else:
            return None
    if isinstance(champ, date):
        return champ
    if isinstance(champ, str):
        champ_nettoye = champ.strip()
        if not champ_nettoye:
            return None
        try:
            return date.fromisoformat(champ_nettoye)
        except ValueError:
            try:
                return datetime.fromisoformat(champ_nettoye).date()
            except ValueError:
                return None
    return None

def parser_depuis_payload(
    donnée: Dict[str, Any], 
    type_objet: Type[TModel], 
    clé_payload: str
) -> TModel:
    payload = donnée.get(clé_payload, donnée)
    return type_objet.model_validate(payload)