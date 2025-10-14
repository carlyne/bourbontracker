from __future__ import annotations

from datetime import date, datetime
from typing import Any
from sqlalchemy import text, Computed, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import Date, DateTime, String, Text

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
    code_type: Mapped[str | None] = mapped_column(String(50))
    libelle: Mapped[str | None] = mapped_column(Text)
    libelle_edition: Mapped[str | None] = mapped_column("libelle_edition", Text)
    libelle_abrege: Mapped[str | None] = mapped_column("libelle_abrege", Text)
    libelle_abrev: Mapped[str | None] = mapped_column("libelle_abrev", String(255))
    organe_parent: Mapped[str | None] = mapped_column("organe_parent", String(255))
    preseance: Mapped[str | None] = mapped_column(String(50))
    organe_precedent_ref: Mapped[str | None] = mapped_column("organe_precedent_ref", String(255))
    vimode_date_debut: Mapped[date | None] = mapped_column("vimode_date_debut", Date)
    vimode_date_agrement: Mapped[date | None] = mapped_column("vimode_date_agrement", Date)
    vimode_date_fin: Mapped[date | None] = mapped_column("vimode_date_fin", Date)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    __table_args__ = (
        Index("ix_organe_code_type", "code_type"),
        Index("ix_organe_libelle", "libelle"),
    )

    @property
    def codeType(self) -> str | None:  # pragma: no cover - simple property
        return self.code_type

    @property
    def libelleEdition(self) -> str | None:  # pragma: no cover - simple property
        return self.libelle_edition

    @property
    def libelleAbrege(self) -> str | None:  # pragma: no cover - simple property
        return self.libelle_abrege

    @property
    def libelleAbrev(self) -> str | None:  # pragma: no cover - simple property
        return self.libelle_abrev

    @property
    def organeParent(self) -> str | None:  # pragma: no cover - simple property
        return self.organe_parent

    @property
    def organePrecedentRef(self) -> str | None:  # pragma: no cover - simple property
        return self.organe_precedent_ref

    @property
    def viMoDe(self) -> dict[str, date | None] | None:  # pragma: no cover - simple property
        if not any((self.vimode_date_debut, self.vimode_date_agrement, self.vimode_date_fin)):
            return None
        return {
            "dateDebut": self.vimode_date_debut,
            "dateAgrement": self.vimode_date_agrement,
            "dateFin": self.vimode_date_fin,
        }

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