"""hash spotify user id

Revision ID: 37eaf9fce33b
Revises: 45e1fea54d92
Create Date: 2026-09-02 09:09:29.088606

"""
import hashlib
import hmac
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '37eaf9fce33b'
down_revision: Union[str, Sequence[str], None] = '45e1fea54d92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Erst umbenennen (Rename statt drop+add -- Daten bleiben erhalten, sonst
    # scheitert add_column NOT NULL ohne Default an den bestehenden Zeilen).
    op.alter_column('users', 'spotify_user_id', new_column_name='spotify_id_hash')
    op.execute('ALTER TABLE users RENAME CONSTRAINT users_spotify_user_id_key TO users_spotify_id_hash_key')

    # Danach die (noch im Klartext stehenden) bestehenden Werte durch ihren
    # HMAC-Hash ersetzen -- mit demselben Secret/Verfahren wie
    # backend.services.pseudonymization.hash_spotify_id, damit sich Nutzer
    # beim naechsten Login wiederfinden statt einen doppelten Account anzulegen.
    from backend.config import settings

    connection = op.get_bind()
    users = sa.table('users', sa.column('id', sa.Integer), sa.column('spotify_id_hash', sa.String))
    rows = connection.execute(sa.select(users.c.id, users.c.spotify_id_hash)).fetchall()

    for row in rows:
        hashed = hmac.new(
            settings.USER_ID_HASH_SECRET.encode(),
            row.spotify_id_hash.encode(),
            hashlib.sha256,
        ).hexdigest()
        connection.execute(
            users.update().where(users.c.id == row.id).values(spotify_id_hash=hashed)
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Hash laesst sich nicht zurueckrechnen -- Downgrade stellt nur die Spalte
    # wieder her, nicht die urspruenglichen Klartextwerte.
    op.execute('ALTER TABLE users RENAME CONSTRAINT users_spotify_id_hash_key TO users_spotify_user_id_key')
    op.alter_column('users', 'spotify_id_hash', new_column_name='spotify_user_id')
