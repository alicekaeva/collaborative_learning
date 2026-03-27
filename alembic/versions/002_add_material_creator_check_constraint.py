"""Add CHECK constraint to materials: exactly one creator (user or group)

Revision ID: 002
Revises: 001
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_material_exactly_one_creator",
        "materials",
        "(creator_user_id IS NOT NULL AND creator_group_id IS NULL)"
        " OR (creator_user_id IS NULL AND creator_group_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_material_exactly_one_creator", "materials", type_="check"
    )
