from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Chrono(BaseModel):
    model_config = ConfigDict(extra="ignore")

    date_creation: Optional[datetime] = Field(alias="dateCreation", default=None)
    date_depot: Optional[datetime] = Field(alias="dateDepot", default=None)
    date_publication: Optional[datetime] = Field(alias="datePublication", default=None)
    date_publication_web: Optional[datetime] = Field(alias="datePublicationWeb", default=None)

