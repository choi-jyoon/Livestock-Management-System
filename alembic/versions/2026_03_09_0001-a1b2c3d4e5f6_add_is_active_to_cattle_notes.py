"""add is_active to cattle_notes

Revision ID: a1b2c3d4e5f6
Revises: 46a283a4db6d
Create Date: 2026-03-09 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '46a283a4db6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # cattle_notes 테이블에 is_active 컬럼 추가 (기존 데이터는 모두 True로 설정)
    op.add_column(
        'cattle_notes',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true())
    )


def downgrade() -> None:
    op.drop_column('cattle_notes', 'is_active')
