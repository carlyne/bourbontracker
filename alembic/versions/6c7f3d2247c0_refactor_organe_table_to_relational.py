"""Refactor organe table to relational columns

Revision ID: 6c7f3d2247c0
Revises: 2a3f1f080d30
Create Date: 2024-05-06 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "6c7f3d2247c0"
down_revision = "2a3f1f080d30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_organe_payload_gin", table_name="organe")

    op.add_column("organe", sa.Column("code_type", sa.String(length=50), nullable=True))
    op.add_column("organe", sa.Column("libelle", sa.Text(), nullable=True))
    op.add_column("organe", sa.Column("libelle_edition", sa.Text(), nullable=True))
    op.add_column("organe", sa.Column("libelle_abrege", sa.Text(), nullable=True))
    op.add_column("organe", sa.Column("libelle_abrev", sa.String(length=255), nullable=True))
    op.add_column("organe", sa.Column("organe_parent", sa.String(length=255), nullable=True))
    op.add_column("organe", sa.Column("preseance", sa.String(length=50), nullable=True))
    op.add_column("organe", sa.Column("organe_precedent_ref", sa.String(length=255), nullable=True))
    op.add_column("organe", sa.Column("vimode_date_debut", sa.Date(), nullable=True))
    op.add_column("organe", sa.Column("vimode_date_agrement", sa.Date(), nullable=True))
    op.add_column("organe", sa.Column("vimode_date_fin", sa.Date(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE organe
            SET
                code_type = NULLIF(btrim(payload ->> 'codeType'), ''),
                libelle = NULLIF(btrim(payload ->> 'libelle'), ''),
                libelle_edition = NULLIF(btrim(payload ->> 'libelleEdition'), ''),
                libelle_abrege = NULLIF(btrim(payload ->> 'libelleAbrege'), ''),
                libelle_abrev = NULLIF(btrim(payload ->> 'libelleAbrev'), ''),
                organe_parent = NULLIF(btrim(payload ->> 'organeParent'), ''),
                preseance = NULLIF(btrim(payload ->> 'preseance'), ''),
                organe_precedent_ref = NULLIF(btrim(payload ->> 'organePrecedentRef'), ''),
                vimode_date_debut = NULLIF(payload -> 'viMoDe' ->> 'dateDebut', '')::date,
                vimode_date_agrement = NULLIF(payload -> 'viMoDe' ->> 'dateAgrement', '')::date,
                vimode_date_fin = NULLIF(payload -> 'viMoDe' ->> 'dateFin', '')::date
            """
        )
    )

    op.drop_column("organe", "payload")

    op.create_index("ix_organe_code_type", "organe", ["code_type"], unique=False)
    op.create_index("ix_organe_libelle", "organe", ["libelle"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_organe_libelle", table_name="organe")
    op.drop_index("ix_organe_code_type", table_name="organe")

    op.add_column(
        "organe",
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.execute(
        sa.text(
            """
            UPDATE organe
            SET payload = jsonb_strip_nulls(
                jsonb_build_object(
                    'uid', uid,
                    'codeType', code_type,
                    'libelle', libelle,
                    'libelleEdition', libelle_edition,
                    'libelleAbrege', libelle_abrege,
                    'libelleAbrev', libelle_abrev,
                    'organeParent', organe_parent,
                    'preseance', preseance,
                    'organePrecedentRef', organe_precedent_ref,
                    'viMoDe', CASE
                        WHEN vimode_date_debut IS NOT NULL
                             OR vimode_date_agrement IS NOT NULL
                             OR vimode_date_fin IS NOT NULL
                        THEN jsonb_strip_nulls(
                            jsonb_build_object(
                                'dateDebut', to_char(vimode_date_debut, 'YYYY-MM-DD'),
                                'dateAgrement', to_char(vimode_date_agrement, 'YYYY-MM-DD'),
                                'dateFin', to_char(vimode_date_fin, 'YYYY-MM-DD')
                            )
                        )
                        ELSE NULL
                    END
                )
            )
            """
        )
    )

    op.alter_column("organe", "payload", nullable=False)
    op.create_index("ix_organe_payload_gin", "organe", ["payload"], unique=False, postgresql_using="gin")

    op.drop_column("organe", "vimode_date_fin")
    op.drop_column("organe", "vimode_date_agrement")
    op.drop_column("organe", "vimode_date_debut")
    op.drop_column("organe", "organe_precedent_ref")
    op.drop_column("organe", "preseance")
    op.drop_column("organe", "organe_parent")
    op.drop_column("organe", "libelle_abrev")
    op.drop_column("organe", "libelle_abrege")
    op.drop_column("organe", "libelle_edition")
    op.drop_column("organe", "libelle")
    op.drop_column("organe", "code_type")

