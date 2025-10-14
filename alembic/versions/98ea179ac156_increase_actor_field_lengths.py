"""increase actor field lengths

Revision ID: 98ea179ac156
Revises: 01457cb07296
Create Date: 2025-10-14 19:41:56.256442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98ea179ac156'
down_revision: Union[str, None] = '01457cb07296'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "acteurv2",
        "categorie_socio_professionnelle",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "acteurv2",
        "famille_socio_professionnelle",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "mandat",
        "infos_qualite_code",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "mandat",
        "infos_qualite_code",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "acteurv2",
        "famille_socio_professionnelle",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "acteurv2",
        "categorie_socio_professionnelle",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
