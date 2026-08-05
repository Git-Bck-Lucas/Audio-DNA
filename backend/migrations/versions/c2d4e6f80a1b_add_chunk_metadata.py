"""add dimension/trait metadata to chunks

Revision ID: c2d4e6f80a1b
Revises: ab1c89f3dc93
Create Date: 2026-07-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c2d4e6f80a1b'
down_revision: Union[str, Sequence[str], None] = 'ab1c89f3dc93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default '{}' (leeres Postgres-Array) füllt bestehende Zeilen, damit NOT NULL hält.
    # Beim nächsten Ingest werden die Zeilen ohnehin ersetzt (replace_chunks) und real getaggt.
    op.add_column('chunks', sa.Column('dimensions', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'))
    op.add_column('chunks', sa.Column('traits', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'))


def downgrade() -> None:
    op.drop_column('chunks', 'traits')
    op.drop_column('chunks', 'dimensions')
