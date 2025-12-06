"""create initial tables with gdpr compliance

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-12-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS hr_core")
    op.execute("CREATE SCHEMA IF NOT EXISTS hr_audit")
    op.execute("CREATE SCHEMA IF NOT EXISTS hr_analytics")
    
    # Create enums
    op.execute("""
        CREATE TYPE hr_core.user_role_enum AS ENUM (
            'admin', 'hr_manager', 'recruiter', 'interviewer', 'readonly'
        )
    """)
    
    op.execute("""
        CREATE TYPE hr_core.job_status_enum AS ENUM (
            'draft', 'published', 'paused', 'closed', 'archived'
        )
    """)
    
    op.execute("""
        CREATE TYPE hr_core.application_status_enum AS ENUM (
            'submitted', 'screening', 'interview_scheduled', 
            'interview_completed', 'shortlisted', 'rejected', 
            'offer_extended', 'hired', 'withdrawn'
        )
    """)
    
    op.execute("""
        CREATE TYPE hr_core.seniority_level_enum AS ENUM (
            'intern', 'junior', 'mid', 'senior', 'lead', 'manager', 'director'
        )
    """)
    
    op.execute("""
        CREATE TYPE hr_core.document_type_enum AS ENUM (
            'resume', 'cover_letter', 'portfolio', 'certificate', 'other'
        )
    """)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'hr_manager', 'recruiter', 'interviewer', 'readonly', name='user_role_enum'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('consent_status', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True)),
        sa.Column('failed_login_attempts', sa.Integer(), default=0),
        sa.Column('locked_until', sa.TIMESTAMP(timezone=True)),
        sa.Column('password_reset_token', sa.String(255)),
        sa.Column('password_reset_expires', sa.TIMESTAMP(timezone=True)),
        schema='hr_core'
    )
    
    # Create candidates table with encrypted PII
    op.create_table('candidates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('encrypted_email', sa.LargeBinary(), nullable=False),
        sa.Column('encrypted_phone', sa.LargeBinary()),
        sa.Column('encrypted_full_name', sa.LargeBinary(), nullable=False),
        sa.Column('encrypted_address', sa.LargeBinary()),
        sa.Column('experience_years', sa.Integer()),
        sa.Column('current_position', sa.String(255)),
        sa.Column('current_company', sa.String(255)),
        sa.Column('skills', postgresql.JSONB(), default=sa.text("'[]'::jsonb")),
        sa.Column('education', postgresql.JSONB(), default=sa.text("'{}'::jsonb")),
        sa.Column('ai_analysis', postgresql.JSONB()),
        sa.Column('skills_extracted', postgresql.JSONB(), default=sa.text("'[]'::jsonb")),
        sa.Column('consent_status', postgresql.JSONB(), nullable=False),
        sa.Column('data_retention_date', sa.Date()),
        sa.Column('gdpr_flags', postgresql.JSONB(), default=sa.text("'{}'::jsonb")),
        sa.Column('source', sa.String(100)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        schema='hr_core'
    )
    
    # Create indexes for performance
    op.create_index('idx_candidates_retention_date', 'candidates', ['data_retention_date'], schema='hr_core')
    op.create_index('idx_candidates_created_at', 'candidates', ['created_at'], schema='hr_core')
    op.create_index('idx_users_email', 'users', ['email'], schema='hr_core')
    op.create_index('idx_users_username', 'users', ['username'], schema='hr_core')


def downgrade() -> None:
    # Drop tables
    op.drop_table('candidates', schema='hr_core')
    op.drop_table('users', schema='hr_core')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS hr_core.user_role_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS hr_core.job_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS hr_core.application_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS hr_core.seniority_level_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS hr_core.document_type_enum CASCADE")
    
    # Drop schemas
    op.execute("DROP SCHEMA IF EXISTS hr_analytics CASCADE")
    op.execute("DROP SCHEMA IF EXISTS hr_audit CASCADE")
    op.execute("DROP SCHEMA IF EXISTS hr_core CASCADE")