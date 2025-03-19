"""add tenant_id and user_id columns

Revision ID: xxx
Revises: previous_revision
Create Date: YYYY-MM-DD HH:MM:SS.SSSSSS
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        
        if 'tenant_id' not in columns:
            op.add_column(table, sa.Column('tenant_id', sa.String(), nullable=False, server_default='default'))
            op.create_index(f'ix_{table}_tenant_id', table, ['tenant_id'])
            
        if 'user_id' not in columns:
            op.add_column(table, sa.Column('user_id', sa.String(), nullable=False, server_default='default'))
            op.create_index(f'ix_{table}_user_id', table, ['user_id'])
        
        # After data migration, remove the server_default
        op.alter_column(table, 'tenant_id', server_default=None)
        op.alter_column(table, 'user_id', server_default=None)

def downgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    for table in tables:
        op.drop_index(f'ix_{table}_tenant_id', table_name=table)
        op.drop_index(f'ix_{table}_user_id', table_name=table)
        op.drop_column(table, 'tenant_id')
        op.drop_column(table, 'user_id') 