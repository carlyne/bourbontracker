from __future__ import annotations

from typing import Any
from datetime import datetime
from sqlalchemy import text, Computed, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import String, DateTime

class Models(DeclarativeBase):
    pass

class Acteur(Models):
    __tablename__ = "acteur"

    uid: Mapped[str] = mapped_column(primary_key=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    organe_refs_jsonb: Mapped[dict] = mapped_column(
        JSONB,
        Computed("jsonb_path_query_array(payload, '$.**.organeRef')", persisted=True)
    )

    __table_args__ = (
        Index("ix_acteur_payload_gin", "payload", postgresql_using="gin"),
        Index("ix_acteur_organe_refs_gin", "organe_refs_jsonb", postgresql_using="gin"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )


class Organe(Models):
    __tablename__ = "organe"
    uid: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    __table_args__ = (
        Index("ix_organe_payload_gin", "payload", postgresql_using="gin"),
    )

class Document(Models):
    __tablename__ = "document"
    uid: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    __table_args__ = (
        Index("ix_document_payload_gin", "payload", postgresql_using="gin"),
    )