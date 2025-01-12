"""products

Revision ID: 627695abb072
Revises: init_schema
Create Date: 2025-01-06 11:18:12.943949

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "627695abb072"
down_revision: Union[str, None] = "init_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP TYPE IF EXISTS productstatus")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
    op.execute("DROP TYPE IF EXISTS subscriptiontype")
    op.execute("DROP TYPE IF EXISTS subscriptionmode")

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
        sa.UniqueConstraint("name", name="uq_product_name"),
    )
    op.create_table(
        "product_subscriptions",
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("wallet_id", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", name="subscriptionstatus"),
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
    # ### end Alembic commands ###


def downgrade() -> None:
    # Drop tables in reverse order with IF EXISTS checks
    op.execute("DROP TABLE IF EXISTS product_credit_settings")
    op.execute("DROP TABLE IF EXISTS product_subscriptions")
    op.execute("DROP TABLE IF EXISTS products")

    # Drop enum types (already has IF EXISTS)
    op.execute("DROP TYPE IF EXISTS productstatus")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
    op.execute("DROP TYPE IF EXISTS subscriptiontype")
    op.execute("DROP TYPE IF EXISTS subscriptionmode")
