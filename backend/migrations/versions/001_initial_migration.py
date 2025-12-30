"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('subscription_tier', sa.String(length=20), nullable=False, server_default='basic'),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_subscription_tier', 'users', ['subscription_tier'])

    # Create communities table
    op.create_table(
        'communities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('access_token_encrypted', sa.Text(), nullable=True),
        sa.Column('refresh_token_encrypted', sa.Text(), nullable=True),
        sa.Column('bot_token_encrypted', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_communities_user_id', 'communities', ['user_id'])
    op.create_index('idx_communities_platform', 'communities', ['platform'])
    op.create_index('idx_communities_external_id', 'communities', ['external_id'])
    op.create_index('idx_communities_active', 'communities', ['user_id', 'is_active', 'deleted_at'])
    op.create_index('idx_communities_token_expires', 'communities', ['token_expires_at'], postgresql_where=sa.text('token_expires_at IS NOT NULL'))

    # Create posts table
    op.create_table(
        'posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('image_storage_path', sa.String(length=500), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_posts_user_id', 'posts', ['user_id'])
    op.create_index('idx_posts_status', 'posts', ['status'])
    op.create_index('idx_posts_user_status', 'posts', ['user_id', 'status'])
    op.create_index('idx_posts_scheduled_at', 'posts', ['scheduled_at'], postgresql_where=sa.text('scheduled_at IS NOT NULL'))
    op.create_index('idx_posts_scheduled_pending', 'posts', ['scheduled_at', 'status'], postgresql_where=sa.text("status = 'scheduled'"))

    # Create post_publications table
    op.create_table(
        'post_publications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('community_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('external_post_id', sa.String(length=255), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'community_id', name='unique_post_community')
    )
    op.create_index('idx_post_publications_post_id', 'post_publications', ['post_id'])
    op.create_index('idx_post_publications_community_id', 'post_publications', ['community_id'])
    op.create_index('idx_post_publications_status', 'post_publications', ['status'])
    op.create_index('idx_post_publications_pending', 'post_publications', ['post_id', 'status'], postgresql_where=sa.text("status = 'pending'"))
    op.create_index('idx_post_publications_external_id', 'post_publications', ['community_id', 'external_post_id'], postgresql_where=sa.text('external_post_id IS NOT NULL'))

    # Create analytics_snapshots table
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('community_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.String(length=50), nullable=False),
        sa.Column('metric_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metric_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_analytics_snapshots_community_id', 'analytics_snapshots', ['community_id'])
    op.create_index('idx_analytics_snapshots_recorded_at', 'analytics_snapshots', ['recorded_at'])
    op.create_index('idx_analytics_snapshots_metric', 'analytics_snapshots', ['community_id', 'metric_name', 'recorded_at'])
    op.create_index('idx_analytics_snapshots_latest', 'analytics_snapshots', ['community_id', 'recorded_at'])

    # Create scheduled_tasks table
    op.create_table(
        'scheduled_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('community_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scheduled_tasks_scheduled_at', 'scheduled_tasks', ['scheduled_at'])
    op.create_index('idx_scheduled_tasks_status', 'scheduled_tasks', ['status'])
    op.create_index('idx_scheduled_tasks_celery_id', 'scheduled_tasks', ['celery_task_id'], postgresql_where=sa.text('celery_task_id IS NOT NULL'))
    op.create_index('idx_scheduled_tasks_pending', 'scheduled_tasks', ['scheduled_at', 'status'], postgresql_where=sa.text("status = 'pending'"))
    op.create_index('idx_scheduled_tasks_post_id', 'scheduled_tasks', ['post_id'], postgresql_where=sa.text('post_id IS NOT NULL'))
    op.create_index('idx_scheduled_tasks_community_id', 'scheduled_tasks', ['community_id'], postgresql_where=sa.text('community_id IS NOT NULL'))


def downgrade() -> None:
    op.drop_table('scheduled_tasks')
    op.drop_table('analytics_snapshots')
    op.drop_table('post_publications')
    op.drop_table('posts')
    op.drop_table('communities')
    op.drop_table('users')
