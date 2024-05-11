"""add content column to posts table

Revision ID: 8197afa8be0e
Revises: b6beb1f702cc
Create Date: 2024-05-10 20:30:40.258630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8197afa8be0e'
down_revision: Union[str, None] = 'b6beb1f702cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
