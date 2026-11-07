"""add chunk embeddings

Revision ID: 546cd405e680
Revises: d6dab957d6bc
Create Date: 2026-11-07 22:52:45.976576

"""
from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import Vector
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '546cd405e680'
down_revision: Union[str, Sequence[str], None] = 'd6dab957d6bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("chunks", sa.Column("chunk_embedding", Vector(2048), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("chunks", "chunk_embedding")
