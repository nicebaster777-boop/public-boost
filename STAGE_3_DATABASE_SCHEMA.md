# Stage 3: Database Schema Design

## Overview

This document defines the complete database schema for the MVP, including all tables, fields, data types, constraints, indexes, and relationships. The schema is designed for PostgreSQL 16.

**Design Principles:**
- All timestamps stored in UTC
- Soft deletes for user data (preserve history)
- Encrypted storage for sensitive tokens
- Indexes optimized for common query patterns
- Foreign key constraints for referential integrity

---

## Table Definitions

### 1. users

Stores user accounts and authentication information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email (login) |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| subscription_tier | VARCHAR(20) | NOT NULL, DEFAULT 'basic' | Subscription tier: 'basic' or 'extended' |
| timezone | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | User's timezone (e.g., 'Europe/Moscow') |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Account active status |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_users_email` on `email` (unique index, created automatically)
- `idx_users_subscription_tier` on `subscription_tier` (for feature gating queries)

**Notes:**
- `subscription_tier` uses VARCHAR for flexibility (can add more tiers later)
- `timezone` stored as IANA timezone identifier (e.g., 'Europe/Moscow', 'UTC')
- `password_hash` uses bcrypt (60+ characters)

---

### 2. communities

Stores connected social media communities (VK groups, Telegram channels).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique community identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) ON DELETE CASCADE | Owner of the community |
| platform | VARCHAR(20) | NOT NULL, CHECK (platform IN ('vk', 'telegram')) | Platform type |
| external_id | VARCHAR(255) | NOT NULL | Platform-specific ID (VK group ID, Telegram channel username) |
| name | VARCHAR(255) | NOT NULL | Display name of the community |
| access_token_encrypted | TEXT | | Encrypted VK access token (NULL for Telegram) |
| refresh_token_encrypted | TEXT | | Encrypted VK refresh token (NULL for Telegram) |
| bot_token_encrypted | TEXT | | Encrypted Telegram bot token (NULL for VK) |
| token_expires_at | TIMESTAMP WITH TIME ZONE | | VK token expiration time (NULL for Telegram or if no expiration) |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Community connection active status |
| last_sync_at | TIMESTAMP WITH TIME ZONE | | Last successful analytics sync timestamp |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Connection creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | TIMESTAMP WITH TIME ZONE | | Soft delete timestamp (NULL if not deleted) |

**Indexes:**
- `idx_communities_user_id` on `user_id` (for user's communities queries)
- `idx_communities_platform` on `platform` (for platform-specific queries)
- `idx_communities_external_id` on `external_id` (for external API lookups)
- `idx_communities_active` on `(user_id, is_active, deleted_at)` (for active communities queries)
- `idx_communities_token_expires` on `token_expires_at` WHERE `token_expires_at IS NOT NULL` (for token refresh queries)

**Unique Constraints:**
- `unique_user_platform_external_id` on `(user_id, platform, external_id)` WHERE `deleted_at IS NULL` (prevent duplicate connections)

**Notes:**
- Soft delete: `deleted_at IS NULL` means active, `deleted_at IS NOT NULL` means deleted
- Tokens encrypted at application level before storage (use encryption library)
- `external_id` format: VK uses numeric ID, Telegram uses username (e.g., '@channelname')
- `token_expires_at` only relevant for VK (Telegram bot tokens don't expire)

---

### 3. posts

Stores user-created posts for scheduling and publishing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique post identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) ON DELETE CASCADE | Post creator |
| content_text | TEXT | NOT NULL | Post text content (max 10,000 chars for VK) |
| image_url | VARCHAR(500) | | URL/path to uploaded image (NULL if no image) |
| image_storage_path | VARCHAR(500) | | Filesystem path to image file (NULL if no image) |
| scheduled_at | TIMESTAMP WITH TIME ZONE | | Scheduled publication time (NULL for draft) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft', CHECK (status IN ('draft', 'scheduled', 'publishing', 'published', 'failed', 'partially_published')) | Post lifecycle status |
| error_message | TEXT | | Error details if status is 'failed' |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Post creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_posts_user_id` on `user_id` (for user's posts queries)
- `idx_posts_status` on `status` (for status-based queries)
- `idx_posts_scheduled_at` on `scheduled_at` WHERE `scheduled_at IS NOT NULL` (for scheduled posts queries)
- `idx_posts_user_status` on `(user_id, status)` (for user's posts by status)
- `idx_posts_scheduled_pending` on `(scheduled_at, status)` WHERE `status = 'scheduled'` (for worker queries)

**Notes:**
- `content_text` max length enforced at application level (VK limit: 10,000 chars)
- `image_url` for external URLs, `image_storage_path` for local filesystem storage
- `scheduled_at` must be in future and within 30 days (enforced at application level)
- Status transitions: draft → scheduled → publishing → published/failed/partially_published
- `partially_published` means some communities succeeded, some failed

---

### 4. post_publications

Stores individual publication records for each post-community pair.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique publication identifier |
| post_id | UUID | NOT NULL, FOREIGN KEY → posts(id) ON DELETE CASCADE | Associated post |
| community_id | UUID | NOT NULL, FOREIGN KEY → communities(id) ON DELETE RESTRICT | Target community |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending', CHECK (status IN ('pending', 'publishing', 'success', 'failed')) | Publication status |
| external_post_id | VARCHAR(255) | | Platform post ID after successful publication |
| published_at | TIMESTAMP WITH TIME ZONE | | Actual publication timestamp (when status = 'success') |
| error_message | TEXT | | Error details if status = 'failed' |
| retry_count | INTEGER | NOT NULL, DEFAULT 0 | Number of retry attempts |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Publication record creation |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_post_publications_post_id` on `post_id` (for post's publications)
- `idx_post_publications_community_id` on `community_id` (for community's publications)
- `idx_post_publications_status` on `status` (for status-based queries)
- `idx_post_publications_pending` on `(post_id, status)` WHERE `status = 'pending'` (for worker queries)
- `idx_post_publications_external_id` on `(community_id, external_post_id)` WHERE `external_post_id IS NOT NULL` (for duplicate check)

**Unique Constraints:**
- `unique_post_community` on `(post_id, community_id)` (one publication per post-community pair)

**Notes:**
- One Post can have multiple PostPublications (one per target community)
- `external_post_id` format: VK uses numeric ID, Telegram uses message ID
- `retry_count` tracks retry attempts (max 3, enforced at application level)
- `published_at` only set when `status = 'success'`

---

### 5. analytics_snapshots

Stores historical analytics data for communities.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique snapshot identifier |
| community_id | UUID | NOT NULL, FOREIGN KEY → communities(id) ON DELETE CASCADE | Associated community |
| metric_name | VARCHAR(50) | NOT NULL | Metric identifier (e.g., 'follower_count', 'engagement_rate') |
| metric_value | NUMERIC(15, 2) | NOT NULL | Metric value |
| recorded_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Snapshot timestamp |
| metadata | JSONB | | Additional metric data (platform-specific) |

**Indexes:**
- `idx_analytics_snapshots_community_id` on `community_id` (for community's snapshots)
- `idx_analytics_snapshots_recorded_at` on `recorded_at` (for time-based queries)
- `idx_analytics_snapshots_metric` on `(community_id, metric_name, recorded_at)` (for metric history)
- `idx_analytics_snapshots_latest` on `(community_id, recorded_at DESC)` (for latest snapshot queries)

**Notes:**
- Append-only table (no updates, only inserts)
- `metric_name` examples: 'follower_count', 'subscriber_count', 'engagement_rate', 'avg_reach', 'avg_likes'
- `metric_value` uses NUMERIC for precise decimal values
- `metadata` JSONB for platform-specific data (e.g., VK post engagement breakdown)
- Retention: Keep 90 days, then archive/delete (background job)

---

### 6. scheduled_tasks (Optional - for MVP reliability)

Stores scheduled task metadata for recovery and tracking.

**Decision**: Store in database for MVP reliability (Redis can lose data on restart).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| task_type | VARCHAR(50) | NOT NULL, CHECK (task_type IN ('publish_post', 'fetch_analytics', 'refresh_token')) | Task type |
| post_id | UUID | FOREIGN KEY → posts(id) ON DELETE CASCADE | Associated post (NULL for non-post tasks) |
| community_id | UUID | FOREIGN KEY → communities(id) ON DELETE CASCADE | Associated community (NULL for non-community tasks) |
| scheduled_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Task execution time |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending', CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')) | Task status |
| celery_task_id | VARCHAR(255) | | Celery task ID (for tracking in Celery) |
| error_message | TEXT | | Error details if status = 'failed' |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_scheduled_tasks_scheduled_at` on `scheduled_at` (for task scheduling queries)
- `idx_scheduled_tasks_status` on `status` (for status-based queries)
- `idx_scheduled_tasks_post_id` on `post_id` WHERE `post_id IS NOT NULL` (for post tasks)
- `idx_scheduled_tasks_community_id` on `community_id` WHERE `community_id IS NOT NULL` (for community tasks)
- `idx_scheduled_tasks_pending` on `(scheduled_at, status)` WHERE `status = 'pending'` (for worker queries)
- `idx_scheduled_tasks_celery_id` on `celery_task_id` WHERE `celery_task_id IS NOT NULL` (for Celery tracking)

**Notes:**
- Tasks stored in both Redis (for Celery) and database (for recovery)
- `celery_task_id` links database record to Celery task
- `status = 'cancelled'` for manually cancelled tasks
- Cleanup: Delete completed tasks older than 7 days (background job)

---

## Data Types and Constraints Summary

### Enums (Implemented as CHECK constraints)

**subscription_tier**: 'basic', 'extended'
**platform**: 'vk', 'telegram'
**post_status**: 'draft', 'scheduled', 'publishing', 'published', 'failed', 'partially_published'
**publication_status**: 'pending', 'publishing', 'success', 'failed'
**task_type**: 'publish_post', 'fetch_analytics', 'refresh_token'
**task_status**: 'pending', 'running', 'completed', 'failed', 'cancelled'

### Common Patterns

- **UUID primary keys**: All tables use UUID for primary keys (better for distributed systems, security)
- **Timestamps**: All timestamps use `TIMESTAMP WITH TIME ZONE` stored in UTC
- **Soft deletes**: `deleted_at` pattern for communities (preserve history)
- **Status fields**: VARCHAR with CHECK constraints (flexible, can add new statuses)
- **Encrypted fields**: TEXT type for encrypted tokens (application-level encryption)

---

## Relationships Diagram

```
users (1) ──< (N) communities
users (1) ──< (N) posts
posts (1) ──< (N) post_publications
communities (1) ──< (N) post_publications
communities (1) ──< (N) analytics_snapshots
posts (1) ──< (0..N) scheduled_tasks
communities (1) ──< (0..N) scheduled_tasks
```

---

## Index Strategy

### Primary Indexes (Automatic)
- All PRIMARY KEY columns have automatic unique indexes

### Foreign Key Indexes
- All foreign key columns indexed for JOIN performance

### Query-Optimized Indexes
- Composite indexes for common query patterns:
  - `(user_id, status)` for user's posts by status
  - `(community_id, metric_name, recorded_at)` for analytics history
  - `(scheduled_at, status)` for worker task queries

### Partial Indexes
- Indexes with WHERE clauses for filtered queries:
  - `scheduled_at` WHERE `scheduled_at IS NOT NULL`
  - `status` WHERE `status = 'pending'` or `status = 'scheduled'`

---

## Security Considerations

### Encryption
- **Tokens**: `access_token_encrypted`, `refresh_token_encrypted`, `bot_token_encrypted` must be encrypted before storage
- **Passwords**: `password_hash` uses bcrypt (application-level hashing)

### Access Control
- All queries must filter by `user_id` to ensure data isolation
- Soft-deleted communities (`deleted_at IS NOT NULL`) excluded from active queries
- Foreign key constraints prevent orphaned records

---

## Data Retention Policies

### Analytics Snapshots
- **Retention**: 90 days
- **Cleanup**: Background job deletes snapshots older than 90 days
- **Implementation**: Scheduled Celery task runs daily

### Scheduled Tasks
- **Retention**: 7 days for completed/failed tasks
- **Cleanup**: Background job deletes old completed tasks
- **Implementation**: Scheduled Celery task runs daily

### Posts
- **Retention**: Indefinite (user data)
- **Cleanup**: None (users can delete manually)

### Communities
- **Soft delete**: `deleted_at` set, data retained
- **Hard delete**: Optional, after 30 days of soft delete (future feature)

---

## Migration Strategy

### Initial Migration
1. Create all tables in dependency order:
   - users
   - communities (depends on users)
   - posts (depends on users)
   - post_publications (depends on posts, communities)
   - analytics_snapshots (depends on communities)
   - scheduled_tasks (depends on posts, communities)

2. Create indexes after tables
3. Add constraints and foreign keys
4. Set up triggers for `updated_at` (if using triggers)

### Future Migrations
- Use Alembic for version control
- Never drop columns in production (mark as deprecated first)
- Add new columns as nullable initially, then backfill

---

## Performance Considerations

### Query Patterns
- **User dashboard**: Query user's communities, latest analytics, scheduled posts
- **Post scheduling**: Query posts by `scheduled_at` and `status = 'scheduled'`
- **Analytics aggregation**: Query snapshots by `community_id` and date range
- **Worker tasks**: Query pending tasks by `scheduled_at` and `status`

### Optimization
- Composite indexes match common query patterns
- Partial indexes reduce index size
- JSONB for flexible metadata (indexed if needed)
- Consider materialized views for complex analytics (post-MVP)

---

## Open Questions / Decisions Needed

1. **Image Storage**: 
   - Store images in filesystem or object storage (S3, MinIO)?
   - Recommendation: Filesystem for MVP, object storage for production

2. **Token Encryption**:
   - Which encryption library? (cryptography, pynacl)
   - Recommendation: Use `cryptography` library with Fernet symmetric encryption

3. **Timezone Storage**:
   - Store as IANA identifier (e.g., 'Europe/Moscow') or offset?
   - Decision: IANA identifier (handles DST automatically)

4. **Analytics Metric Names**:
   - Standardize metric names or allow platform-specific?
   - Decision: Standardize common metrics, use metadata JSONB for platform-specific

5. **Scheduled Tasks Table**:
   - Keep in database or rely only on Redis?
   - Decision: Keep in database for reliability (Redis can lose data)

---

## Next Steps

After schema approval:
1. Create Alembic migration files
2. Define SQLAlchemy ORM models
3. Set up database connection and session management
4. Implement encryption utilities for tokens
5. Create database seed data (if needed for development)

---

## Что мне нужно сделать (пошагово)

1. **Просмотреть схему базы данных**: Прочитать `STAGE_3_DATABASE_SCHEMA.md` и проверить все таблицы, поля и связи

2. **Проверить типы данных**: Убедиться, что выбранные типы данных (UUID, TIMESTAMP, VARCHAR, TEXT, JSONB) соответствуют требованиям

3. **Проверить индексы**: Подтвердить, что индексы оптимизированы для запланированных запросов

4. **Ответить на открытые вопросы**: Дать решения по 5 открытым вопросам (image storage, encryption, timezone, metrics, scheduled tasks)

5. **Проверить ограничения**: Убедиться, что CHECK constraints и foreign keys корректны

6. **Подтвердить стратегию миграций**: Согласовать подход к миграциям базы данных (Alembic)

7. **После подтверждения**: Одобрить переход к Stage 4 (API Design) или Stage 5 (Frontend Design), где мы определим API endpoints и структуру фронтенда
