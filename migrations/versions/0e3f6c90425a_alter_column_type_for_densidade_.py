"""Alter column type for densidade_observada

Revision ID: 0e3f6c90425a
Revises: ae41d7ea282a
Create Date: 2024-12-30 15:56:12.461283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e3f6c90425a'
down_revision: Union[str, None] = 'ae41d7ea282a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('densidade_gasolina', 'densidade_observada',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Float(),
                    existing_nullable=False)


def downgrade():
    op.alter_column('densidade_gasolina', 'densidade_observada',
                    existing_type=sa.Float(),
                    type_=sa.VARCHAR(),
                    existing_nullable=False)
