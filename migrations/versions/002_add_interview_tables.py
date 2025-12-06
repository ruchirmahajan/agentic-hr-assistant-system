"""Add interview tables

Revision ID: 002_add_interview_tables
Revises: 001_initial_schema
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '002_add_interview_tables'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create interview_panels table
    op.create_table('interview_panels',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('level', sa.String(50), nullable=False),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('max_interviews_per_day', sa.Integer(), default=5),
        sa.Column('interview_duration_minutes', sa.Integer(), default=60),
        sa.Column('buffer_minutes', sa.Integer(), default=15),
        sa.Column('interviewers', sa.JSON(), default=list),
        sa.Column('skills_evaluated', sa.JSON(), default=list),
        sa.Column('evaluation_criteria', sa.JSON(), default=list),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create interviews table first (before interview_slots to avoid circular FK)
    op.create_table('interviews',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), sa.ForeignKey('candidates.id'), nullable=False),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('application_id', sa.String(36), sa.ForeignKey('applications.id'), nullable=True),
        sa.Column('panel_id', sa.String(36), sa.ForeignKey('interview_panels.id'), nullable=False),
        sa.Column('level', sa.String(50), nullable=False),
        sa.Column('round_number', sa.Integer(), default=1),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interview_mode', sa.String(50), default='video'),
        sa.Column('meeting_link', sa.String(500), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('status', sa.String(20), default='scheduled'),
        sa.Column('feedback', sa.JSON(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('recommendation', sa.String(50), nullable=True),
        sa.Column('interviewer_notes', sa.Text(), nullable=True),
        sa.Column('hr_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(36), nullable=True),
    )
    
    # Create interview_slots table
    op.create_table('interview_slots',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('panel_id', sa.String(36), sa.ForeignKey('interview_panels.id'), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(20), default='available'),
        sa.Column('interview_id', sa.String(36), sa.ForeignKey('interviews.id'), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), default=False),
        sa.Column('recurrence_pattern', sa.String(50), nullable=True),
        sa.Column('recurrence_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create interview_feedback table
    op.create_table('interview_feedback',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('interview_id', sa.String(36), sa.ForeignKey('interviews.id'), nullable=False),
        sa.Column('interviewer_id', sa.String(36), nullable=False),
        sa.Column('interviewer_name', sa.String(200), nullable=False),
        sa.Column('interviewer_role', sa.String(100), nullable=True),
        sa.Column('scores', sa.JSON(), default=dict),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('weaknesses', sa.Text(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.String(50), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create indexes
    op.create_index('ix_interview_panels_level', 'interview_panels', ['level'])
    op.create_index('ix_interview_panels_is_active', 'interview_panels', ['is_active'])
    op.create_index('ix_interview_slots_panel_id', 'interview_slots', ['panel_id'])
    op.create_index('ix_interview_slots_status', 'interview_slots', ['status'])
    op.create_index('ix_interview_slots_date', 'interview_slots', ['date'])
    op.create_index('ix_interviews_candidate_id', 'interviews', ['candidate_id'])
    op.create_index('ix_interviews_job_id', 'interviews', ['job_id'])
    op.create_index('ix_interviews_panel_id', 'interviews', ['panel_id'])
    op.create_index('ix_interviews_status', 'interviews', ['status'])
    op.create_index('ix_interviews_scheduled_date', 'interviews', ['scheduled_date'])
    op.create_index('ix_interview_feedback_interview_id', 'interview_feedback', ['interview_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_interview_feedback_interview_id')
    op.drop_index('ix_interviews_scheduled_date')
    op.drop_index('ix_interviews_status')
    op.drop_index('ix_interviews_panel_id')
    op.drop_index('ix_interviews_job_id')
    op.drop_index('ix_interviews_candidate_id')
    op.drop_index('ix_interview_slots_date')
    op.drop_index('ix_interview_slots_status')
    op.drop_index('ix_interview_slots_panel_id')
    op.drop_index('ix_interview_panels_is_active')
    op.drop_index('ix_interview_panels_level')
    
    # Drop tables
    op.drop_table('interview_feedback')
    op.drop_table('interview_slots')
    op.drop_table('interviews')
    op.drop_table('interview_panels')
