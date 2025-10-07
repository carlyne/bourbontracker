"""Utilitaires communs pour les modèles métier."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


def nil_or_text(value: Any) -> Optional[str]:
    """Convertit une valeur pouvant représenter une chaîne ou ``None``."""

    if value is None:
        return None
    if isinstance(value, str):
        stripped_value = value.strip()
        return stripped_value or None
    if isinstance(value, dict):
        if str(value.get("@xsi:nil", "")).lower() == "true":
            return None
        for key in ("#text", "text", "value"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                stripped_candidate = candidate.strip()
                if stripped_candidate:
                    return stripped_candidate
    return None


def ensure_list(value: Any) -> List[Any]:
    """Garantit qu'une valeur est représentée sous forme de séquence."""

    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def parse_model_from_payload(
    data: Dict[str, Any], model_cls: Type[TModel], payload_key: str
) -> TModel:
    """Extrait un modèle depuis un dictionnaire de payload."""

    payload = data.get(payload_key, data)
    return model_cls.model_validate(payload)

