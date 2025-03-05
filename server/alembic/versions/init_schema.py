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
    op.execute("DROP TYPE IF EXISTS productstatus")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
    op.execute("DROP TYPE IF EXISTS subscriptiontype")
    op.execute("DROP TYPE IF EXISTS subscriptionmode")

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
        sa.Column("external_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_wallets_external_id", "external_id", unique=True),
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
        sa.Column("external_id", sa.String(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", "wallet_id"),
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
            "ix_transactions_external_id",
            "external_id",
            "wallet_id",
            unique=True,
        ),
        sa.Index("ix_transactions_wallet_id", "wallet_id", unique=False),
        sa.Index("ix_transactions_subscription_id", "subscription_id", unique=False),
        sa.Index("ix_transactions_created_at", "created_at", unique=False),
    )

    create_partitioned_table(
        table_name="transactions", partition_column="wallet_id", num_partitions=10
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
        sa.PrimaryKeyConstraint("id", "wallet_id"),
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

    create_partitioned_table(
        table_name="balances", partition_column="wallet_id", num_partitions=10
    )

    op.create_table(
        "products",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", name="productstatus"),
            nullable=False,
        ),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "product_subscriptions",
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("wallet_id", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "ACTIVE",
                "COMPLETED",
                "CANCELLED",
                "FAILED",
                name="subscriptionstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Enum("ONE_TIME", "RECURRING", name="subscriptiontype"),
            nullable=False,
        ),
        sa.Column(
            "mode",
            sa.Enum("ADD", "RESET", name="subscriptionmode"),
            nullable=False,
        ),
        sa.Column(
            "settings_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["wallet_id"],
            ["wallets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "product_credit_settings",
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("credit_type_id", sa.String(), nullable=False),
        sa.Column("credit_amount", sa.Float(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["credit_type_id"],
            ["credit_types.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "product_id",
            "credit_type_id",
            name="uq_product_credit_type",
        ),
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table("balances")
    op.drop_table("transactions")
    op.drop_table("credit_types")
    op.drop_table("wallets")
    op.drop_table("product_credit_settings")
    op.drop_table("product_subscriptions")
    op.drop_table("products")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS holdstatus")
    op.execute("DROP TYPE IF EXISTS transactionstatus")
    op.execute("DROP TYPE IF EXISTS walletstatus")
    op.execute("DROP TYPE IF EXISTS productstatus")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
    op.execute("DROP TYPE IF EXISTS subscriptiontype")
    op.execute("DROP TYPE IF EXISTS subscriptionmode")


def create_partitioned_table(table_name, partition_column, num_partitions=10):
    """
    Convert a table to a partitioned table by hash of the specified column
    and create the specified number of partitions.

    Args:
        op: Alembic operations object
        table_name: Name of the table to partition
        partition_column: Column to use for partitioning
        num_partitions: Number of partitions to create (default: 10)
    """
    # First, we need to drop the original table but save its definition
    op.execute(
        f"""
        CREATE TABLE {table_name}_temp (LIKE {table_name} INCLUDING ALL);
        DROP TABLE {table_name} CASCADE;

        CREATE TABLE {table_name} (
            LIKE {table_name}_temp INCLUDING ALL
        ) PARTITION BY HASH ({partition_column});

        DROP TABLE {table_name}_temp;
        """
    )

    # Create partitions
    for i in range(num_partitions):
        op.execute(
            f"""
            CREATE TABLE {table_name}_part_{i} PARTITION OF {table_name}
            FOR VALUES WITH (modulus {num_partitions}, remainder {i});
            """
        )
