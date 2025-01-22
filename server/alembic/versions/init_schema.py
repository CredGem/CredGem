"""init_schema

Revision ID: init_schema
Revises: 
Create Date: 2024-12-29 11:38:59.021403
"""
from re import T
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "init_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First try to drop the enum types if they exist
    op.execute("DROP TYPE IF EXISTS transactiontype CASCADE")
    op.execute("DROP TYPE IF EXISTS holdstatus")
    op.execute("DROP TYPE IF EXISTS transactionstatus")
    op.execute("DROP TYPE IF EXISTS walletstatus")

    # Create wallets table
    op.create_table(
        "wallets",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", name="walletstatus"),
            nullable=False,
            default="ACTIVE",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create credit_types table
    op.create_table(
        "credit_types",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create transactions table
    op.create_table(
        "transactions",
        sa.Column(
            "type",
            sa.Enum(
                "DEPOSIT", "DEBIT", "HOLD", "RELEASE", "ADJUST", name="transactiontype"
            ),
            nullable=False,
        ),
        sa.Column("external_transaction_id", sa.String(), nullable=True),
        sa.Column("wallet_id", sa.String(), nullable=False),
        sa.Column("credit_type_id", sa.String(), nullable=False),
        sa.Column("issuer", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "hold_status",
            sa.Enum("HELD", "USED", "RELEASED", "EXPIRED", name="holdstatus"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", name="transactionstatus"),
            nullable=False,
        ),
        sa.Column("balance_snapshot", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("subscription_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["wallet_id"], ["wallets.id"], name="transactions_wallet_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["credit_type_id"],
            ["credit_types.id"],
            name="transactions_credit_type_id_fkey",
        ),
        sa.Index("ix_transactions_credit_type_id", "credit_type_id", unique=False),
        sa.Index(
            "ix_transactions_external_transaction_id",
            "external_transaction_id",
            unique=True,
        ),
        sa.Index("ix_transactions_wallet_id", "wallet_id", unique=False),
        sa.Index("ix_transactions_subscription_id", "subscription_id", unique=False),
    )

    # Create balances table
    op.create_table(
        "balances",
        sa.Column("wallet_id", sa.String(), nullable=False),
        sa.Column("credit_type_id", sa.String(), nullable=False),
        sa.Column("available", sa.Float(), nullable=False),
        sa.Column("held", sa.Float(), nullable=False),
        sa.Column("spent", sa.Float(), nullable=False),
        sa.Column("overall_spent", sa.Float(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["wallet_id"], ["wallets.id"], name="balances_wallet_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["credit_type_id"], ["credit_types.id"], name="balances_credit_type_id_fkey"
        ),
        sa.Index("ix_balances_credit_type_id", "credit_type_id", unique=False),
        sa.Index("ix_balances_wallet_id", "wallet_id", unique=False),
        sa.Index(
            "ix_balances_wallet_credit_composite",
            "wallet_id",
            "credit_type_id",
            unique=True,
        ),
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table("balances")
    op.drop_table("transactions")
    op.drop_table("credit_types")
    op.drop_table("wallets")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS holdstatus")
    op.execute("DROP TYPE IF EXISTS transactionstatus")
    op.execute("DROP TYPE IF EXISTS walletstatus")
