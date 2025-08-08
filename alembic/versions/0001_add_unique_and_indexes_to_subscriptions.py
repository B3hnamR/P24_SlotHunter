"""
Add unique constraint and indexes to subscriptions

Revision ID: 0001
Revises: None
Create Date: 2025-08-07
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply unique/indexes with data cleanup for existing duplicates."""
    bind = op.get_bind()

    # Clean up duplicate rows before creating a unique index
    # Keep the newest row per (user_id, doctor_id) based on created_at (fallback to max(id))
    try:
        duplicates = list(bind.execute(sa.text(
            """
            SELECT user_id, doctor_id, COUNT(*) AS c
            FROM subscriptions
            GROUP BY user_id, doctor_id
            HAVING c > 1
            """
        )))

        for row in duplicates:
            user_id = row[0]
            doctor_id = row[1]
            # Find the row to keep (newest by created_at, fallback id)
            keep_row = bind.execute(sa.text(
                """
                SELECT id
                FROM subscriptions
                WHERE user_id = :user_id AND doctor_id = :doctor_id
                ORDER BY COALESCE(created_at, '1970-01-01') DESC, id DESC
                LIMIT 1
                """
            ), {"user_id": user_id, "doctor_id": doctor_id}).fetchone()
            keep_id = keep_row[0] if keep_row else None

            if keep_id is not None:
                bind.execute(sa.text(
                    """
                    DELETE FROM subscriptions
                    WHERE user_id = :user_id AND doctor_id = :doctor_id AND id != :keep_id
                    """
                ), {"user_id": user_id, "doctor_id": doctor_id, "keep_id": keep_id})
    except Exception:
        # Best-effort cleanup; do not fail migration due to cleanup step
        pass

    # On SQLite, create_unique_constraint may map to unique index; use create_index with unique=True for portability
    op.create_index('uq_subscription_user_doctor', 'subscriptions', ['user_id', 'doctor_id'], unique=True)
    op.create_index('ix_subscriptions_user_active', 'subscriptions', ['user_id', 'is_active'], unique=False)


def downgrade() -> None:
    # Drop indexes
    try:
        op.drop_index('ix_subscriptions_user_active', table_name='subscriptions')
    except Exception:
        pass
    try:
        op.drop_index('uq_subscription_user_doctor', table_name='subscriptions')
    except Exception:
        pass
