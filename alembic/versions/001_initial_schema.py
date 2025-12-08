"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-12-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: Enum types are automatically created by SQLAlchemy when the tables are created
    # No need to manually create them here

    # Create scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenarios_name'), 'scenarios', ['name'], unique=False)

    # Create simulation_runs table
    op.create_table(
        'simulation_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', name='simulationstatus'), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('results_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('config_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_simulation_runs_scenario_id'), 'simulation_runs', ['scenario_id'], unique=False)
    op.create_index(op.f('ix_simulation_runs_status'), 'simulation_runs', ['status'], unique=False)
    op.create_index(op.f('ix_simulation_runs_created_at'), 'simulation_runs', ['created_at'], unique=False)

    # Create comparisons table
    op.create_table(
        'comparisons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('scenario_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', name='simulationstatus'), nullable=False),
        sa.Column('results_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comparisons_created_at'), 'comparisons', ['created_at'], unique=False)

    # Create imported_datasets table
    op.create_table(
        'imported_datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', sa.Enum('github', 'gitlab', 'csv', name='importsourcetype'), nullable=False),
        sa.Column('source_name', sa.String(length=255), nullable=False),
        sa.Column('import_date', sa.DateTime(), nullable=False),
        sa.Column('metrics_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('suggested_config_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('raw_data_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_imported_datasets_source_type'), 'imported_datasets', ['source_type'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_imported_datasets_source_type'), table_name='imported_datasets')
    op.drop_table('imported_datasets')

    op.drop_index(op.f('ix_comparisons_created_at'), table_name='comparisons')
    op.drop_table('comparisons')

    op.drop_index(op.f('ix_simulation_runs_created_at'), table_name='simulation_runs')
    op.drop_index(op.f('ix_simulation_runs_status'), table_name='simulation_runs')
    op.drop_index(op.f('ix_simulation_runs_scenario_id'), table_name='simulation_runs')
    op.drop_table('simulation_runs')

    op.drop_index(op.f('ix_scenarios_name'), table_name='scenarios')
    op.drop_table('scenarios')

    # Drop enum types
    op.execute("DROP TYPE importsourcetype")
    op.execute("DROP TYPE simulationstatus")
