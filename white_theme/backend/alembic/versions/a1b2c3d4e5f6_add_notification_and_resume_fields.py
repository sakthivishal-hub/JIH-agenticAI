"""add notification and resume fields

Revision ID: a1b2c3d4e5f6
Revises: 916266ca2d4c
Create Date: 2026-07-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '916266ca2d4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('resume_text', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('whatsapp_number', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('notify_email', sa.Boolean(), nullable=True, server_default=sa.true()))
    op.add_column('users', sa.Column('notify_whatsapp', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'notify_whatsapp')
    op.drop_column('users', 'notify_email')
    op.drop_column('users', 'whatsapp_number')
    op.drop_column('users', 'resume_text')
