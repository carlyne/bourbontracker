from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Notice(BaseModel):
    model_config = ConfigDict(extra="ignore")

    num_notice: Optional[str] = Field(alias="numNotice", default=None)
    formule: Optional[str] = None
    adoption_conforme: Optional[str] = Field(alias="adoptionConforme", default=None)
