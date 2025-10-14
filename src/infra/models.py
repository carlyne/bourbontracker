from __future__ import annotations

from typing import Any
from datetime import date, datetime
from sqlalchemy import text, Computed, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    __table_args__ = (
        Index("ix_organe_payload_gin", "payload", postgresql_using="gin"),
    )

class OrganeV2(Models):
    __tablename__ = "organev2"

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
    def codeType(self) -> str | None:  
        return self.code_type

    @property
    def libelleEdition(self) -> str | None:  
        return self.libelle_edition

    @property
    def libelleAbrege(self) -> str | None:  
        return self.libelle_abrege

    @property
    def libelleAbrev(self) -> str | None:  
        return self.libelle_abrev

    @property
    def organeParent(self) -> str | None:  
        return self.organe_parent

    @property
    def organePrecedentRef(self) -> str | None:  
        return self.organe_precedent_ref

    @property
    def viMoDe(self) -> dict[str, date | None] | None:  
        if not any((self.vimode_date_debut, self.vimode_date_agrement, self.vimode_date_fin)):
            return None
        return {
            "dateDebut": self.vimode_date_debut,
            "dateAgrement": self.vimode_date_agrement,
            "dateFin": self.vimode_date_fin,
        }
    
class ActeurV2(Models):
    __tablename__ = "acteurv2"

    uid: Mapped[str] = mapped_column(String, primary_key=True)
    civilite: Mapped[str | None] = mapped_column(String(10))
    prenom: Mapped[str | None] = mapped_column(String(255))
    nom: Mapped[str | None] = mapped_column(String(255))
    date_naissance: Mapped[date | None] = mapped_column(Date)
    ville_naissance: Mapped[str | None] = mapped_column(String(255))
    departement_naissance: Mapped[str | None] = mapped_column(String(255))
    pays_naissance: Mapped[str | None] = mapped_column(String(255))
    date_deces: Mapped[date | None] = mapped_column(Date)
    profession_libelle: Mapped[str | None] = mapped_column(Text)
    categorie_socio_professionnelle: Mapped[str | None] = mapped_column(String(50))
    famille_socio_professionnelle: Mapped[str | None] = mapped_column(String(50))
    url_fiche_acteur: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    mandats: Mapped[list["Mandat"]] = relationship(
        back_populates="acteur", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_acteurv2_nom", "nom"),
        Index("ix_acteurv2_prenom", "prenom"),
    )


class Mandat(Models):
    __tablename__ = "mandat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid: Mapped[str | None] = mapped_column(String(255), unique=True)
    acteur_uid: Mapped[str] = mapped_column(
        String, ForeignKey("acteurv2.uid", ondelete="CASCADE"), nullable=False
    )
    organe_uid: Mapped[str | None] = mapped_column(
        String, ForeignKey("organev2.uid", ondelete="SET NULL"), nullable=True
    )
    legislature: Mapped[str | None] = mapped_column(String(50))
    type_organe: Mapped[str | None] = mapped_column(String(50))
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_publication: Mapped[date | None] = mapped_column(Date)
    date_fin: Mapped[date | None] = mapped_column(Date)
    preseance: Mapped[str | None] = mapped_column(String(50))
    nomin_principale: Mapped[str | None] = mapped_column(String(255))
    infos_qualite_code: Mapped[str | None] = mapped_column(String(50))
    infos_qualite_libelle: Mapped[str | None] = mapped_column(Text)
    infos_qualite_libelle_sexe: Mapped[str | None] = mapped_column(Text)
    chambre: Mapped[str | None] = mapped_column(String(50))
    cause_mandat: Mapped[str | None] = mapped_column(String(255))
    ref_circonscription: Mapped[str | None] = mapped_column(String(255))
    lieu_region: Mapped[str | None] = mapped_column(String(255))
    lieu_region_type: Mapped[str | None] = mapped_column(String(50))
    lieu_departement: Mapped[str | None] = mapped_column(String(255))
    lieu_num_departement: Mapped[str | None] = mapped_column(String(10))
    lieu_num_circonscription: Mapped[str | None] = mapped_column(String(10))
    mandature_date_prise_fonction: Mapped[date | None] = mapped_column(Date)
    mandature_cause_fin: Mapped[str | None] = mapped_column(String(255))
    mandature_premiere_election: Mapped[str | None] = mapped_column(String(255))
    mandature_place_hemicycle: Mapped[str | None] = mapped_column(String(50))
    mandature_mandat_remplace_ref: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    acteur: Mapped[ActeurV2] = relationship(back_populates="mandats")
    organe: Mapped[OrganeV2 | None] = relationship()
    collaborateurs: Mapped[list["Collaborateur"]] = relationship(
        back_populates="mandat", cascade="all, delete-orphan"
    )
    suppleants: Mapped[list["Suppleant"]] = relationship(
        back_populates="mandat", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_mandat_acteur_uid", "acteur_uid"),
        Index("ix_mandat_organe_uid", "organe_uid"),
        Index("ix_mandat_legislature", "legislature"),
    )


class Collaborateur(Models):
    __tablename__ = "collaborateur"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mandat_id: Mapped[int] = mapped_column(
        ForeignKey("mandat.id", ondelete="CASCADE"), nullable=False
    )
    qualite: Mapped[str | None] = mapped_column(String(255))
    prenom: Mapped[str | None] = mapped_column(String(255))
    nom: Mapped[str | None] = mapped_column(String(255))
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin: Mapped[date | None] = mapped_column(Date)

    mandat: Mapped[Mandat] = relationship(back_populates="collaborateurs")


class Suppleant(Models):
    __tablename__ = "suppleant"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mandat_id: Mapped[int] = mapped_column(
        ForeignKey("mandat.id", ondelete="CASCADE"), nullable=False
    )
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin: Mapped[date | None] = mapped_column(Date)
    suppleant_uid: Mapped[str | None] = mapped_column(String(255))

    mandat: Mapped[Mandat] = relationship(back_populates="suppleants")

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