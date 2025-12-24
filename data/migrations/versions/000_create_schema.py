"""Create predecessor schema

Revision ID: 000
Revises:
Create Date: 2024-12-23

Creates the predecessor schema where all application tables live.
The alembic_version table remains in the public schema.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the predecessor schema if it doesn't exist
    # This is idempotent - safe to run even if schema already exists
    op.execute("CREATE SCHEMA IF NOT EXISTS predecessor")


def downgrade() -> None:
    # WARNING: This will drop all tables in the schema!
    # Only run this if you really want to remove everything
    op.execute("DROP SCHEMA IF EXISTS predecessor CASCADE")
