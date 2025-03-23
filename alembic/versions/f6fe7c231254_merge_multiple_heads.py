"""Merge multiple heads

Revision ID: f6fe7c231254
Revises: 0e5e42d28b5d, ae9c1a7f9769
Create Date: 2025-03-23 12:19:21.774051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6fe7c231254'
down_revision: Union[str, None] = ('0e5e42d28b5d', 'ae9c1a7f9769')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
