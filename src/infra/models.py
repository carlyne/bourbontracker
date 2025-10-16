from __future__ import annotations

from typing import Any
from datetime import date, datetime
from sqlalchemy import text, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.types import Date, DateTime, Integer, String, Text

class Models(DeclarativeBase):
    pass

class OrganeModel(Models):
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
    
class ActeurModel(Models):
    __tablename__ = "acteur"

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
    categorie_socio_professionnelle: Mapped[str | None] = mapped_column(String(255))
    famille_socio_professionnelle: Mapped[str | None] = mapped_column(String(255))
    url_fiche_acteur: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    mandats: Mapped[list["MandatModel"]] = relationship(
        back_populates="acteur", cascade="all, delete-orphan"
    )

    documents: Mapped[list["DocumentActeurModel"]] = relationship(
        back_populates="acteur"
    )

    __table_args__ = (
        Index("ix_acteur_nom", "nom"),
        Index("ix_acteur_prenom", "prenom"),
    )


class MandatModel(Models):
    __tablename__ = "mandat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid: Mapped[str | None] = mapped_column(String(255), unique=True)
    acteur_uid: Mapped[str] = mapped_column(
        String, ForeignKey("acteur.uid", ondelete="CASCADE"), nullable=False
    )
    organe_uid: Mapped[str | None] = mapped_column(
        String, ForeignKey("organe.uid", ondelete="SET NULL"), nullable=True
    )
    legislature: Mapped[str | None] = mapped_column(String(50))
    type_organe: Mapped[str | None] = mapped_column(String(50))
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_publication: Mapped[date | None] = mapped_column(Date)
    date_fin: Mapped[date | None] = mapped_column(Date)
    preseance: Mapped[str | None] = mapped_column(String(50))
    nomin_principale: Mapped[str | None] = mapped_column(String(255))
    infos_qualite_code: Mapped[str | None] = mapped_column(String(255))
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

    acteur: Mapped[ActeurModel] = relationship(back_populates="mandats")
    organe: Mapped[OrganeModel | None] = relationship()
    collaborateurs: Mapped[list["CollaborateurModel"]] = relationship(
        back_populates="mandat", cascade="all, delete-orphan"
    )
    suppleants: Mapped[list["SuppleantModel"]] = relationship(
        back_populates="mandat", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_mandat_acteur_uid", "acteur_uid"),
        Index("ix_mandat_organe_uid", "organe_uid"),
        Index("ix_mandat_legislature", "legislature"),
    )


class CollaborateurModel(Models):
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

    mandat: Mapped[MandatModel] = relationship(back_populates="collaborateurs")


class SuppleantModel(Models):
    __tablename__ = "suppleant"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mandat_id: Mapped[int] = mapped_column(
        ForeignKey("mandat.id", ondelete="CASCADE"), nullable=False
    )
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin: Mapped[date | None] = mapped_column(Date)
    suppleant_uid: Mapped[str | None] = mapped_column(String(255))

    mandat: Mapped[MandatModel] = relationship(back_populates="suppleants")

class DocumentModel(Models):
    __tablename__ = "document"

    uid: Mapped[str] = mapped_column(String, primary_key=True)
    legislature: Mapped[str | None] = mapped_column(String(50))
    titre_principal: Mapped[str | None] = mapped_column(Text)
    titre_principal_court: Mapped[str | None] = mapped_column(Text)
    denomination_structurelle: Mapped[str | None] = mapped_column(Text)
    provenance: Mapped[str | None] = mapped_column(Text)
    notice_num_notice: Mapped[str | None] = mapped_column(String(255))
    notice_formule: Mapped[str | None] = mapped_column(Text)
    notice_adoption_conforme: Mapped[str | None] = mapped_column(Text)
    classification_famille_depot_code: Mapped[str | None] = mapped_column(String(50))
    classification_famille_depot_libelle: Mapped[str | None] = mapped_column(Text)
    classification_famille_classe_code: Mapped[str | None] = mapped_column(String(50))
    classification_famille_classe_libelle: Mapped[str | None] = mapped_column(Text)
    classification_famille_espece_code: Mapped[str | None] = mapped_column(String(50))
    classification_famille_espece_libelle: Mapped[str | None] = mapped_column(Text)
    classification_famille_espece_libelle_edition: Mapped[str | None] = mapped_column(Text)
    classification_type_code: Mapped[str | None] = mapped_column(String(50))
    classification_type_libelle: Mapped[str | None] = mapped_column(Text)
    classification_sous_type_code: Mapped[str | None] = mapped_column(String(50))
    classification_sous_type_libelle: Mapped[str | None] = mapped_column(Text)
    classification_sous_type_libelle_edition: Mapped[str | None] = mapped_column(Text)
    classification_statut_adoption: Mapped[str | None] = mapped_column(Text)
    date_creation: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_depot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_publication: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_publication_web: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    organes_referents: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    dossier_ref: Mapped[str | None] = mapped_column(String(255))
    redacteur: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    auteurs: Mapped[list["DocumentActeurModel"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentActeur.ordre",
    )

    __table_args__ = (
        Index("ix_document_date_creation", "date_creation"),
        Index("ix_document_date_depot", "date_depot"),
        Index("ix_document_date_publication", "date_publication"),
    )


class DocumentActeurModel(Models):
    __tablename__ = "document_acteur"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_uid: Mapped[str] = mapped_column(
        String, ForeignKey("document.uid", ondelete="CASCADE"), nullable=False
    )
    acteur_uid: Mapped[str | None] = mapped_column(
        String, ForeignKey("acteur.uid", ondelete="SET NULL"), nullable=True
    )
    acteur_ref: Mapped[str | None] = mapped_column(String(255))
    qualite: Mapped[str | None] = mapped_column(String(255))
    ordre: Mapped[int | None] = mapped_column(Integer)

    document: Mapped[DocumentModel] = relationship(back_populates="auteurs")
    acteur: Mapped[ActeurModel | None] = relationship(back_populates="documents")

    __table_args__ = (
        Index("ix_document_acteur_document_uid", "document_uid"),
        Index("ix_document_acteur_acteur_uid", "acteur_uid"),
    )