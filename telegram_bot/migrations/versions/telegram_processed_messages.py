"""add telegram processed messages

Revision ID: telegram_processed_messages
Revises: 6ea787151d0b
Create Date: 2026-06-13
"""

from alembic import op
import sqlalchemy as sa


revision = "telegram_processed_messages"
down_revision = "6ea787151d0b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_processed_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=True),
        sa.Column("message_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="processing"),
        sa.Column("jira_key", sa.String(length=64), nullable=True),
        sa.Column("jira_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("chat_id", "message_id", name="uq_telegram_processed_chat_message"),
    )


def downgrade() -> None:
    op.drop_table("telegram_processed_messages")