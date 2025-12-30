# Stage 2: System Architecture and Core Entities

## 1. High-Level System Architecture

### Component Overview

The system consists of five main components that interact through well-defined interfaces:

```
┌─────────────┐
│  Frontend   │ (React + Vite)
│  (Browser)  │
└──────┬──────┘
       │ HTTP/REST
       │ JWT Auth
       ▼
┌─────────────────────────────────────┐
│         Backend API                 │
│         (FastAPI)                   │
│  ┌───────────────────────────────┐  │
│  │  Authentication Layer         │  │
│  │  Business Logic Layer         │  │
│  │  API Integration Layer        │  │
│  └───────────────────────────────┘  │
└──────┬──────────────────┬───────────┘
       │                  │
       │ SQL              │ Queue Messages
       ▼                  ▼
┌─────────────┐    ┌──────────────────┐
│  PostgreSQL │    │  Redis (Queue)   │
│  (Database) │    └────────┬─────────┘
└─────────────┘             │
                            │ Task Messages
                            ▼
                    ┌──────────────────┐
                    │  Celery Workers  │
                    │  (Background)    │
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
          ┌─────────┐  ┌─────────┐  ┌─────────┐
          │ VK API  │  │Telegram │  │Analytics│
          │         │  │Bot API  │  │ Fetcher │
          └─────────┘  └─────────┘  └─────────┘
```

### Component Responsibilities

#### Frontend (React Application)
- **Purpose**: User interface and interaction layer
- **Responsibilities**:
  - Render UI components (dashboard, calendar, post editor)
  - Handle user input and form validation (client-side)
  - Manage client-side state (user session, UI state)
  - Make HTTP requests to backend API
  - Display data received from backend
  - Handle authentication flow (login, token storage)
- **Does NOT**:
  - Store sensitive data (tokens stored in memory/secure storage only)
  - Make direct API calls to VK/Telegram (all go through backend)
  - Execute business logic (validation, calculations)
  - Schedule tasks (backend responsibility)

#### Backend API (FastAPI)
- **Purpose**: Core business logic and API gateway
- **Responsibilities**:
  - Authenticate users (JWT token generation/validation)
  - Authorize requests (subscription tier checks, resource ownership)
  - Execute business logic (post creation, community management)
  - Validate input data (content, scheduling times, file sizes)
  - Coordinate with database (CRUD operations)
  - Enqueue background tasks (post publishing, analytics fetching)
  - Provide REST API endpoints for frontend
  - Handle rate limiting (API-level throttling)
- **Does NOT**:
  - Execute long-running tasks (delegated to workers)
  - Make direct external API calls synchronously (delegated to workers for scheduled operations)
  - Store file uploads permanently (temporary storage, then pass to workers)

#### Database (PostgreSQL)
- **Purpose**: Persistent data storage
- **Responsibilities**:
  - Store user accounts and authentication data
  - Store community connections and credentials
  - Store posts (content, scheduling, status)
  - Store analytics snapshots (historical metrics)
  - Maintain referential integrity
  - Provide transactional guarantees
- **Does NOT**:
  - Execute business logic
  - Cache frequently accessed data (Redis for that)
  - Store large files (use object storage or filesystem)

#### Background Workers (Celery)
- **Purpose**: Asynchronous task execution
- **Responsibilities**:
  - Execute scheduled post publishing (at specified times)
  - Fetch analytics data from VK/Telegram APIs periodically
  - Refresh expired VK access tokens
  - Handle retries for failed operations
  - Manage rate limiting for external APIs (queuing, delays)
  - Update database with results (publication status, analytics data)
- **Does NOT**:
  - Handle user-facing HTTP requests
  - Execute tasks synchronously (always async/queued)
  - Store business logic (logic lives in backend, workers execute it)

#### Message Queue (Redis)
- **Purpose**: Task queue and coordination
- **Responsibilities**:
  - Store pending tasks (post publishing, analytics fetching)
  - Coordinate task distribution among workers
  - Provide task priority and scheduling
  - Store temporary data (rate limit counters, locks)
- **Does NOT**:
  - Store persistent application data
  - Execute tasks (workers do that)
  - Handle business logic

#### External APIs (VK API, Telegram Bot API)
- **Purpose**: Platform integrations
- **Responsibilities**:
  - Provide community data and statistics
  - Accept post publications
  - Provide authentication/authorization (VK OAuth)
- **Constraints**:
  - Rate limits (must be respected)
  - Token expiration (VK tokens expire)
  - Network latency (unpredictable)
  - Service availability (external dependency)

### Data Flow Patterns

#### User Authentication Flow
```
Frontend → Backend API → Database (verify credentials)
Backend API → Frontend (JWT token)
Frontend stores token (memory/localStorage)
```

#### Post Creation Flow
```
Frontend → Backend API (POST /posts with content, schedule time, target communities)
Backend API → Database (store post as "scheduled")
Backend API → Redis Queue (enqueue publishing task for scheduled time)
Backend API → Frontend (confirmation with post ID)
```

#### Post Publishing Flow (Background)
```
Celery Worker (scheduled task triggered) → Database (fetch post details)
Celery Worker → VK API / Telegram Bot API (publish post)
External API → Celery Worker (success/failure response)
Celery Worker → Database (update post status, store publication record)
```

#### Analytics Fetching Flow (Background)
```
Celery Worker (periodic task) → Database (fetch all active communities)
Celery Worker → VK API / Telegram Bot API (request statistics)
External API → Celery Worker (metrics data)
Celery Worker → Database (store analytics snapshot)
```

#### Analytics Display Flow
```
Frontend → Backend API (GET /analytics?community_id=X)
Backend API → Database (fetch latest snapshots)
Backend API → Frontend (aggregated metrics)
```

---

## 2. Core Logical Entities (Conceptual Model)

### Entity: User
- **Purpose**: Represents an authenticated user account in the system
- **Logical meaning**: A person who owns communities and creates posts
- **Key characteristics**:
  - Has unique identity (email-based authentication)
  - Owns subscription tier (Basic or Extended)
  - Owns multiple communities (one-to-many relationship)
  - Creates posts (one-to-many relationship)
- **Relationships**:
  - Owns multiple Communities
  - Creates multiple Posts
  - Has one SubscriptionTier

### Entity: Community
- **Purpose**: Represents a connected social media community (VK group or Telegram channel)
- **Logical meaning**: A platform-specific community that user manages
- **Key characteristics**:
  - Belongs to one User (ownership)
  - Has platform type (VK or Telegram)
  - Has external platform identifier (VK group ID, Telegram channel username)
  - Stores authentication credentials (VK access token, Telegram bot token)
  - Has display name and metadata
- **Relationships**:
  - Belongs to one User
  - Receives multiple PostPublications
  - Has multiple AnalyticsSnapshots
- **Lifecycle**:
  - Created when user connects a community
  - Can be disconnected (soft delete or hard delete)
  - Credentials may expire (VK tokens)

### Entity: Post
- **Purpose**: Represents a content item created by user for publishing
- **Logical meaning**: A piece of content (text + optional image) intended for publication
- **Key characteristics**:
  - Belongs to one User (creator)
  - Has content (text, optional image reference)
  - Has scheduling information (scheduled_at timestamp, timezone)
  - Has lifecycle state (draft, scheduled, publishing, published, failed)
  - Can target multiple communities (one-to-many with PostPublication)
- **Relationships**:
  - Belongs to one User
  - Results in multiple PostPublications (one per target community)
- **Lifecycle states**:
  - **draft**: Created but not scheduled
  - **scheduled**: Scheduled for future publication
  - **publishing**: Currently being published (worker executing)
  - **published**: Successfully published to all target communities
  - **failed**: Failed to publish (after retries)

### Entity: PostPublication
- **Purpose**: Represents a single publication attempt of a Post to a specific Community
- **Logical meaning**: The execution record of publishing one post to one community
- **Key characteristics**:
  - Links one Post to one Community
  - Has publication status (pending, success, failed)
  - Stores external platform post ID (if successful)
  - Records publication timestamp
  - Stores error information (if failed)
- **Relationships**:
  - Belongs to one Post
  - Targets one Community
- **Why separate from Post?**
  - One Post can be published to multiple communities
  - Each publication may succeed or fail independently
  - Need to track individual publication status per community

### Entity: AnalyticsSnapshot
- **Purpose**: Represents a point-in-time capture of community metrics
- **Logical meaning**: A historical record of community statistics at a specific moment
- **Key characteristics**:
  - Belongs to one Community
  - Has timestamp (when metrics were captured)
  - Contains metric values (follower count, engagement metrics)
  - Metric types vary by platform (VK vs Telegram have different available metrics)
- **Relationships**:
  - Belongs to one Community
- **Lifecycle**:
  - Created periodically by background worker (every 6-12 hours)
  - Retained for historical analysis (retention policy TBD)
  - Used to generate insights (best posting time, top posts)

### Entity: SubscriptionTier
- **Purpose**: Represents user's access level to features
- **Logical meaning**: Determines which features user can access
- **Key characteristics**:
  - Has tier name (Basic, Extended)
  - Defines feature access (analytics only, or analytics + autoposting)
  - Associated with User (one-to-one in MVP)
- **Relationships**:
  - Assigned to one User
- **Note**: In MVP, this is a simple enum/flag, not a separate billing entity

### Entity: ScheduledTask
- **Purpose**: Represents a background job scheduled for execution
- **Logical meaning**: A task queued in Redis/Celery for future execution
- **Key characteristics**:
  - Has task type (publish_post, fetch_analytics, refresh_token)
  - Has scheduled execution time
  - Has task payload (references to Post, Community, etc.)
  - Has execution status (pending, running, completed, failed)
- **Relationships**:
  - May reference Post (for publishing tasks)
  - May reference Community (for analytics/token refresh tasks)
- **Note**: This is primarily a queue concept, may not need persistent storage in MVP

### Entity: IntegrationToken
- **Purpose**: Represents authentication credentials for external platforms
- **Logical meaning**: Stored credentials that allow system to access user's communities
- **Key characteristics**:
  - Belongs to one Community
  - Has token value (encrypted storage)
  - Has expiration time (VK tokens expire)
  - Has refresh token (for VK, if available)
  - Has token type (VK access token, Telegram bot token)
- **Relationships**:
  - Belongs to one Community
- **Security**: Must be encrypted at rest, never exposed to frontend

### Entity Relationships Summary

```
User
  ├── owns → Community (1:N)
  ├── creates → Post (1:N)
  └── has → SubscriptionTier (1:1)

Community
  ├── belongs to → User (N:1)
  ├── receives → PostPublication (1:N)
  ├── has → AnalyticsSnapshot (1:N)
  └── has → IntegrationToken (1:1)

Post
  ├── belongs to → User (N:1)
  └── results in → PostPublication (1:N)

PostPublication
  ├── belongs to → Post (N:1)
  └── targets → Community (N:1)

AnalyticsSnapshot
  └── belongs to → Community (N:1)

ScheduledTask
  ├── may reference → Post (optional)
  └── may reference → Community (optional)
```

---

## 3. Responsibility Boundaries

### Backend Responsibilities

#### Authentication & Authorization
- User registration and login
- JWT token generation and validation
- Password hashing and verification
- Subscription tier validation (feature gating)
- Resource ownership verification (user can only access their own data)

#### Business Logic
- Post creation validation (content length, file size, scheduling time)
- Community connection validation (verify user has admin rights)
- Subscription tier enforcement (block autoposting for Basic tier)
- Data aggregation for analytics (calculate insights from snapshots)
- Timezone handling (convert user timezone to UTC for storage)

#### Data Management
- CRUD operations for all entities
- Transaction management (ensure data consistency)
- Data validation (input sanitization, format checking)
- Referential integrity enforcement

#### Task Coordination
- Enqueue background tasks (post publishing, analytics fetching)
- Schedule tasks for future execution
- Provide task status endpoints (for frontend polling)

#### API Integration (Coordination Only)
- Validate integration credentials before enqueueing tasks
- Store integration tokens securely
- Coordinate token refresh (enqueue refresh tasks)

### Frontend Responsibilities

#### User Interface
- Render all UI components (forms, lists, calendars, charts)
- Handle user interactions (clicks, form submissions, navigation)
- Display data received from backend
- Show loading states and error messages

#### Client-Side Validation
- Form field validation (required fields, format checking)
- File size validation before upload
- Date/time picker validation (prevent past dates, enforce 30-day limit)
- Real-time feedback (character count, file preview)

#### State Management
- User session state (logged in user, JWT token)
- UI state (selected community, active tab, form data)
- Cache frequently accessed data (communities list, recent posts)
- Optimistic updates (show scheduled post immediately, update on confirmation)

#### API Communication
- Make HTTP requests to backend
- Handle HTTP errors (401, 403, 429, 500)
- Retry failed requests (with exponential backoff)
- Poll for updates (task status, analytics refresh)

#### Does NOT Handle
- Business logic validation (backend does this)
- Direct external API calls (all through backend)
- Background task execution
- Data persistence (backend/database)

### Background Workers Responsibilities

#### External API Communication
- Make actual API calls to VK and Telegram
- Handle API rate limiting (respect limits, implement delays)
- Retry failed API calls (exponential backoff, max 3 attempts)
- Handle API errors (network failures, authentication errors, rate limits)

#### Task Execution
- Execute scheduled post publishing at correct time
- Execute periodic analytics fetching (every 6-12 hours)
- Execute token refresh tasks (before expiration)
- Update database with task results

#### Error Handling
- Log all errors with context
- Update entity status (post → failed, community → disconnected)
- Store error details for user visibility
- Notify system (logs) of critical failures

#### Does NOT Handle
- User-facing HTTP requests
- Business logic decisions (logic in backend, workers execute)
- Authentication (workers use stored credentials)

### Database Responsibilities

#### Data Persistence
- Store all entity data reliably
- Maintain data integrity (foreign keys, constraints)
- Provide transactional guarantees (ACID)
- Support queries for analytics aggregation

#### Does NOT Handle
- Business logic
- API calls
- Task scheduling
- Authentication (only stores hashed passwords)

---

## 4. Data Lifecycle (High Level)

### Analytics Data Lifecycle

#### Creation
- **Trigger**: Periodic background task (every 6-12 hours) or manual refresh request
- **Process**: Worker fetches current metrics from VK/Telegram APIs
- **Storage**: New AnalyticsSnapshot created with current timestamp and metric values
- **Initial State**: Snapshot is "current" (latest for that community)

#### Update
- **Trigger**: New snapshot created (previous snapshot becomes historical)
- **Process**: No modification of existing snapshots (append-only model)
- **Aggregation**: Backend queries multiple snapshots to calculate trends (follower growth, engagement changes)

#### Usage
- **Dashboard Display**: Backend queries latest snapshot per community
- **Insights Generation**: Backend queries historical snapshots (last 30 days) to calculate "best posting time"
- **Trend Analysis**: Backend compares snapshots across time periods

#### Expiration
- **Retention Policy**: TBD (recommendation: keep 90 days for MVP, archive older)
- **Cleanup**: Background task periodically removes snapshots older than retention period
- **Note**: Expiration not critical for MVP, can be implemented later

### Post Lifecycle

#### Creation (draft state)
- **Trigger**: User creates post via frontend
- **Process**: Backend validates content, stores in database as "draft"
- **Storage**: Post entity created with status="draft", scheduled_at=null

#### Scheduling (scheduled state)
- **Trigger**: User sets schedule time and target communities
- **Process**: Backend validates schedule time (future, within 30 days), enqueues task
- **Storage**: Post status="scheduled", scheduled_at set, PostPublication records created
- **Queue**: Task enqueued in Redis for execution at scheduled time

#### Publishing (publishing state)
- **Trigger**: Scheduled time arrives, Celery worker picks up task
- **Process**: Worker updates post status="publishing", makes API calls to each target community
- **Storage**: PostPublication records updated as each publication succeeds/fails
- **Parallelization**: Multiple communities can be published in parallel (with rate limiting)

#### Completion (published or failed state)
- **Success Path**: All PostPublications succeed → Post status="published"
- **Failure Path**: Any PostPublication fails after retries → Post status="failed", error details stored
- **Partial Success**: Some succeed, some fail → Post status="partially_published" (or "failed" if critical)
- **Storage**: Final status stored, external post IDs stored in PostPublication records

#### Post-Publication
- **Historical Record**: Published posts remain in database for history view
- **No Modification**: Published posts cannot be edited (only viewed)
- **Analytics Link**: Future analytics may reference published posts (track engagement)

### Community Connection Lifecycle

#### Connection (active state)
- **Trigger**: User initiates OAuth flow (VK) or adds bot to channel (Telegram)
- **Process**: Backend receives credentials, validates permissions, stores IntegrationToken
- **Storage**: Community entity created, IntegrationToken stored (encrypted)

#### Active Usage
- **Analytics Fetching**: Periodic tasks use IntegrationToken to fetch metrics
- **Post Publishing**: Workers use IntegrationToken to publish posts
- **Token Refresh**: Background task refreshes VK tokens before expiration

#### Disconnection
- **Trigger**: User removes community connection or token expires/invalid
- **Process**: Backend marks community as "disconnected" or deletes it
- **Cleanup**: Scheduled posts targeting disconnected community may be cancelled or marked as failed
- **Storage**: Community soft-deleted or hard-deleted (TBD)

### Error and Retry Lifecycle

#### Error Detection
- **API Errors**: Worker catches HTTP errors, rate limit errors, authentication errors
- **Network Errors**: Timeouts, connection failures
- **Validation Errors**: Invalid content, missing permissions

#### Retry Logic
- **Immediate Retries**: Transient errors (network timeouts) → retry immediately (max 3 attempts)
- **Delayed Retries**: Rate limit errors → retry after delay (exponential backoff)
- **No Retry**: Permanent errors (invalid credentials, content violation) → mark as failed immediately

#### Error Storage
- **Post Level**: Post status="failed", error message stored
- **Publication Level**: PostPublication status="failed", specific error per community
- **Community Level**: Community marked as "error" if credentials invalid

#### User Notification
- **Frontend Polling**: Frontend polls task status, displays errors in UI
- **Error Display**: Failed posts shown in calendar/history with error details
- **Manual Retry**: User can manually retry failed posts (creates new task)

---

## 5. Risks and Architectural Constraints

### Architectural Risks

#### 1. Single Point of Failure: Database
- **Risk**: PostgreSQL failure stops entire system
- **Impact**: All operations fail (read and write)
- **Mitigation for MVP**: Regular backups, basic monitoring
- **Postponed**: Read replicas, database clustering

#### 2. Task Queue Dependency: Redis
- **Risk**: Redis failure prevents background task execution
- **Impact**: Scheduled posts won't publish, analytics won't update
- **Mitigation for MVP**: Redis persistence enabled, basic monitoring
- **Postponed**: Redis cluster, queue replication

#### 3. External API Dependency
- **Risk**: VK/Telegram API downtime or changes break functionality
- **Impact**: Post publishing fails, analytics unavailable
- **Mitigation**: Graceful error handling, user notifications, retry logic
- **Cannot Mitigate**: External dependency, must handle gracefully

#### 4. Token Expiration Race Condition
- **Risk**: VK token expires between validation and use
- **Impact**: Post publishing fails even though token was valid during scheduling
- **Mitigation**: Refresh tokens proactively (before expiration), retry with refresh on 401 errors
- **Note**: Requires verification of VK token refresh mechanism

#### 5. Rate Limit Violations
- **Risk**: Multiple users scheduling posts simultaneously may exceed API limits
- **Impact**: Posts fail with 429 errors, temporary API access restrictions
- **Mitigation**: Global rate limiting queue, per-community rate limiting, user warnings
- **Complexity**: Requires distributed rate limiting (Redis-based counters)

#### 6. Timezone Handling Complexity
- **Risk**: Incorrect timezone conversion causes posts to publish at wrong time
- **Impact**: User experience degradation, missed publication windows
- **Mitigation**: Store all times in UTC, convert to user timezone only for display
- **Edge Cases**: Daylight saving time transitions, user changing timezone

### API-Related Uncertainties

#### VK API
- **⚠️ VERIFICATION REQUIRED**: Exact rate limits (requests per second/minute)
- **⚠️ VERIFICATION REQUIRED**: Token refresh mechanism and refresh token lifetime
- **⚠️ VERIFICATION REQUIRED**: Analytics API availability and data retention period
- **⚠️ VERIFICATION REQUIRED**: Post scheduling limits (how far in advance can posts be scheduled)

#### Telegram Bot API
- **⚠️ VERIFICATION REQUIRED**: Analytics alternatives (Client API requirements, third-party services)
- **⚠️ VERIFICATION REQUIRED**: Channel vs Group API differences for posting
- **⚠️ VERIFICATION REQUIRED**: Bot token security best practices

### Scaling Concerns (Post-MVP)

#### Database Scaling
- **Current**: Single PostgreSQL instance
- **Future Need**: Read replicas for analytics queries, connection pooling
- **Not MVP**: Optimize for MVP speed, plan for future scaling

#### Worker Scaling
- **Current**: Single or few Celery workers
- **Future Need**: Horizontal scaling (multiple workers, load balancing)
- **Not MVP**: Start with single worker, scale as needed

#### Rate Limiting at Scale
- **Current**: Basic per-community rate limiting
- **Future Need**: Global rate limiting across all users, priority queues
- **Not MVP**: Basic implementation sufficient

### Reliability Concerns

#### Task Loss
- **Risk**: Redis failure during task execution may lose pending tasks
- **Impact**: Scheduled posts never publish
- **Mitigation for MVP**: Redis persistence, task acknowledgment, basic monitoring
- **Postponed**: Task persistence in database, task deduplication

#### Duplicate Publishing
- **Risk**: Task executed multiple times (worker crash during execution)
- **Impact**: Post published twice to same community
- **Mitigation**: Idempotency checks (check if post already published before publishing)
- **Implementation**: Store external post ID, check before publishing

#### Data Consistency
- **Risk**: Partial updates (post published to some communities but not all)
- **Impact**: Inconsistent state, user confusion
- **Mitigation**: Transactional updates where possible, clear status indicators
- **Acceptable**: Partial success is acceptable (some communities succeed, some fail)

### Security Concerns

#### Token Storage
- **Risk**: Integration tokens exposed in logs or database dumps
- **Impact**: Unauthorized access to user communities
- **Mitigation**: Encrypt tokens at rest, never log tokens, secure database access
- **Critical**: Must be implemented from start

#### Authentication
- **Risk**: JWT token theft or expiration issues
- **Impact**: Unauthorized access or user lockout
- **Mitigation**: Short token expiration, refresh token mechanism, HTTPS only
- **Standard**: Follow JWT best practices

#### Input Validation
- **Risk**: Malicious content or oversized files cause system issues
- **Impact**: Storage exhaustion, API rejections, security vulnerabilities
- **Mitigation**: Strict validation (file size, content length, format checking)
- **Critical**: Must validate all user input

---

## Clarifications Needed

Before proceeding to Stage 3 (Database Schema Design), please confirm or clarify:

1. **Community Deletion**: Should communities be soft-deleted (marked as deleted, data retained) or hard-deleted (permanently removed)? This affects data retention and user experience.

2. **Post Editing**: Can users edit scheduled posts after creation? If yes, what happens to already-enqueued tasks?

3. **Analytics Retention**: How long should analytics snapshots be retained? (Recommendation: 90 days for MVP)

4. **Timezone Storage**: Should we store user's timezone preference, or detect from browser? (Recommendation: Store user preference)

5. **Partial Publication Handling**: If a post fails for some communities but succeeds for others, should the post be marked as "partially published" or "failed"?

6. **Task Persistence**: Should scheduled tasks be stored in database (for recovery) or only in Redis queue? (Recommendation: Store in database for MVP reliability)

---

## Что мне нужно сделать (пошагово)

1. **Просмотреть документ архитектуры Stage 2**: Прочитать `STAGE_2_ARCHITECTURE.md` и понять структуру системы

2. **Проверить взаимодействие компонентов**: Подтвердить, что паттерны потоков данных соответствуют вашему случаю использования

3. **Проверить основные сущности**: Убедиться, что все необходимые сущности идентифицированы и связи корректны

4. **Уточнить границы ответственности**: Подтвердить, что разделение ответственности между backend/frontend/workers корректно

5. **Ответить на вопросы для уточнения**: Дать ответы на 6 вопросов, перечисленных выше

6. **Выявить недостающие сущности**: Если какие-то логические сущности отсутствуют в концептуальной модели, указать их

7. **Подтвердить архитектурные решения**: Проверить, что выбранные технологии (FastAPI, Celery, Redis, PostgreSQL) соответствуют вашим техническим предпочтениям

8. **Проверить риски**: Признать выявленные риски и подтвердить, что стратегии митигации приемлемы для MVP

9. **После подтверждения**: Одобрить переход к Stage 3 (Проектирование схемы базы данных), где мы определим точные структуры таблиц, поля, индексы и связи

