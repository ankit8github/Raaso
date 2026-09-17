"""add attendance updated at

Revision ID: ff11dcc71303
Revises: dbd753776212
Create Date: 2026-09-17 23:15:27.592547

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ff11dcc71303"
down_revision: Union[str, Sequence[str], None] = "dbd753776212"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "attendances",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE attendances SET updated_at = created_at WHERE updated_at IS NULL"
    )

    op.alter_column(
        "attendances",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("attendances", "updated_at")