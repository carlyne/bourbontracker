"""create acteurv2 relational tables

Revision ID: b5c9b21a2ef1
Revises: e1762abdd751
Create Date: 2025-10-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b5c9b21a2ef1"
down_revision: Union[str, None] = "e1762abdd751"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "acteurv2",
        sa.Column("uid", sa.String(), nullable=False),
        sa.Column("civilite", sa.String(length=10), nullable=True),
        sa.Column("prenom", sa.String(length=255), nullable=True),
        sa.Column("nom", sa.String(length=255), nullable=True),
        sa.Column("date_naissance", sa.Date(), nullable=True),
        sa.Column("ville_naissance", sa.String(length=255), nullable=True),
        sa.Column("departement_naissance", sa.String(length=255), nullable=True),
        sa.Column("pays_naissance", sa.String(length=255), nullable=True),
        sa.Column("date_deces", sa.Date(), nullable=True),
        sa.Column("profession_libelle", sa.Text(), nullable=True),
        sa.Column("categorie_socio_professionnelle", sa.String(length=50), nullable=True),
        sa.Column("famille_socio_professionnelle", sa.String(length=50), nullable=True),
        sa.Column("url_fiche_acteur", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("uid"),
    )
    op.create_index("ix_acteurv2_nom", "acteurv2", ["nom"], unique=False)
    op.create_index("ix_acteurv2_prenom", "acteurv2", ["prenom"], unique=False)

    op.create_table(
        "mandatv2",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uid", sa.String(length=255), nullable=True),
        sa.Column("acteur_uid", sa.String(), nullable=False),
        sa.Column("organe_uid", sa.String(), nullable=True),
        sa.Column("legislature", sa.String(length=50), nullable=True),
        sa.Column("type_organe", sa.String(length=50), nullable=True),
        sa.Column("date_debut", sa.Date(), nullable=True),
        sa.Column("date_publication", sa.Date(), nullable=True),
        sa.Column("date_fin", sa.Date(), nullable=True),
        sa.Column("preseance", sa.String(length=50), nullable=True),
        sa.Column("nomin_principale", sa.String(length=255), nullable=True),
        sa.Column("infos_qualite_code", sa.String(length=50), nullable=True),
        sa.Column("infos_qualite_libelle", sa.Text(), nullable=True),
        sa.Column("infos_qualite_libelle_sexe", sa.Text(), nullable=True),
        sa.Column("chambre", sa.String(length=50), nullable=True),
        sa.Column("cause_mandat", sa.String(length=255), nullable=True),
        sa.Column("ref_circonscription", sa.String(length=255), nullable=True),
        sa.Column("lieu_region", sa.String(length=255), nullable=True),
        sa.Column("lieu_region_type", sa.String(length=50), nullable=True),
        sa.Column("lieu_departement", sa.String(length=255), nullable=True),
        sa.Column("lieu_num_departement", sa.String(length=10), nullable=True),
        sa.Column("lieu_num_circonscription", sa.String(length=10), nullable=True),
        sa.Column("mandature_date_prise_fonction", sa.Date(), nullable=True),
        sa.Column("mandature_cause_fin", sa.String(length=255), nullable=True),
        sa.Column("mandature_premiere_election", sa.String(length=255), nullable=True),
        sa.Column("mandature_place_hemicycle", sa.String(length=50), nullable=True),
        sa.Column("mandature_mandat_remplace_ref", sa.String(length=255), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint([
            "acteur_uid"
        ], [
            "acteurv2.uid"
        ], ondelete="CASCADE"),
        sa.ForeignKeyConstraint([
            "organe_uid"
        ], [
            "organev2.uid"
        ], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uid", name="uq_mandatv2_uid"),
    )
    op.create_index("ix_mandatv2_acteur_uid", "mandatv2", ["acteur_uid"], unique=False)
    op.create_index("ix_mandatv2_legislature", "mandatv2", ["legislature"], unique=False)
    op.create_index("ix_mandatv2_organe_uid", "mandatv2", ["organe_uid"], unique=False)

    op.create_table(
        "collaborateurv2",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mandat_id", sa.Integer(), nullable=False),
        sa.Column("qualite", sa.String(length=255), nullable=True),
        sa.Column("prenom", sa.String(length=255), nullable=True),
        sa.Column("nom", sa.String(length=255), nullable=True),
        sa.Column("date_debut", sa.Date(), nullable=True),
        sa.Column("date_fin", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint([
            "mandat_id"
        ], [
            "mandatv2.id"
        ], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "suppleantv2",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mandat_id", sa.Integer(), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=True),
        sa.Column("date_fin", sa.Date(), nullable=True),
        sa.Column("suppleant_uid", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint([
            "mandat_id"
        ], [
            "mandatv2.id"
        ], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("suppleantv2")
    op.drop_table("collaborateurv2")
    op.drop_index("ix_mandatv2_organe_uid", table_name="mandatv2")
    op.drop_index("ix_mandatv2_legislature", table_name="mandatv2")
    op.drop_index("ix_mandatv2_acteur_uid", table_name="mandatv2")
    op.drop_table("mandatv2")
    op.drop_index("ix_acteurv2_prenom", table_name="acteurv2")
    op.drop_index("ix_acteurv2_nom", table_name="acteurv2")
    op.drop_table("acteurv2")
