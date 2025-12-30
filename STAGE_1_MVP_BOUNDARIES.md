# Stage 1: MVP Boundaries and Technical Constraints

## 1. MVP Scope Definition

### ✅ Included in MVP

#### Analytics Module (Basic Plan)
- **Community connection**: User can connect VK communities and Telegram channels/groups
- **Basic metrics aggregation**:
  - Follower/subscriber count (current snapshot)
  - Post engagement metrics (likes, comments, shares, views) - aggregated per post
  - Simple time-series data (daily/weekly follower growth)
- **Data refresh**: Manual refresh button + automatic background updates (every 6-12 hours)
- **Simple dashboard**: Single view showing all connected communities with key metrics
- **Basic insights** (if data available):
  - "Best posting time" recommendation (based on historical engagement)
  - Top performing posts (last 30 days)

#### Autoposting Module (Extended Plan)
- **Post creation**:
  - Text content (with basic formatting)
  - Single image attachment (VK and Telegram)
  - Link preview (automatic)
- **Scheduling**:
  - Calendar view for scheduled posts
  - Schedule posts up to 30 days in advance
  - Timezone support (user's local timezone)
- **Publishing**:
  - Publish to VK communities (user must be admin/editor)
  - Publish to Telegram channels (bot must be admin)
  - Single post can be published to multiple communities simultaneously
- **Post management**:
  - View scheduled posts
  - Edit/delete scheduled posts (before publication)
  - View published posts history

#### User Management (MVP)
- **Authentication**: Email/password registration and login
- **Single user per account**: No team collaboration in MVP
- **Community management**: User can add/remove connected communities

#### Subscription Model (MVP)
- **Two tiers**: Basic (analytics only) and Extended (analytics + autoposting)
- **Manual subscription management**: Admin panel to assign plans (no payment gateway in MVP)
- **Feature gating**: UI/API restrictions based on subscription tier

### ❌ Explicitly Postponed

#### Analytics
- Real-time data updates
- Advanced analytics (demographics, audience insights, competitor analysis)
- Custom date range selection for historical data
- Export functionality (CSV, PDF reports)
- Data visualization beyond basic charts
- Multi-community comparison dashboards

#### Autoposting
- Video content support
- Multiple images per post (carousels/galleries)
- Polls, quizzes, interactive content
- Post templates and content library
- Recurring posts (daily/weekly schedules)
- A/B testing
- Post preview before scheduling
- Content moderation/approval workflows
- Support for additional platforms (Instagram, Facebook, etc.)

#### User Management
- Team collaboration (multiple users per account)
- Role-based access control
- OAuth login (Google, VK, etc.)
- Two-factor authentication

#### Business Features
- Payment gateway integration (Stripe, PayPal, etc.)
- Automated subscription billing
- Usage-based pricing
- Free trial period automation
- Email notifications
- In-app notifications

#### Technical
- VK Mini App version
- Mobile native apps
- Webhook support for real-time updates
- API for third-party integrations
- Advanced error recovery and retry logic
- Content caching and CDN

---

## 2. API Limitations and Risks

### VK API Constraints

**⚠️ VERIFICATION REQUIRED**: The following information should be confirmed in official VK API documentation (vk.com/dev).

#### Rate Limits
- **General API calls**: VK API has rate limits per application, but exact numbers are not publicly documented
- **Risk**: Exceeding limits can result in temporary API access restrictions (minutes to hours)
- **Mitigation**: Implement request queuing and exponential backoff retry logic

#### Posting to Communities
- **Permissions**: User must have admin or editor rights in the community
- **Post frequency**: No official documented limit, but aggressive posting may trigger spam detection
- **Risk**: Community may be restricted or posts may be hidden if posting behavior looks automated
- **Mitigation**: Respect reasonable posting intervals (minimum 5-10 minutes between posts recommended)

#### Content Restrictions
- **Image size**: Maximum 5 MB per image (verification required)
- **Text length**: Maximum 10,000 characters per post
- **Link previews**: Automatic, but can be disabled
- **Risk**: Content violating VK's terms of service can result in post removal or account restrictions

#### Analytics Data Access
- **Statistics API**: Requires specific permissions (`stats` scope)
- **Data availability**: Historical statistics may be limited (typically 30-90 days)
- **Update frequency**: Statistics are not real-time, updates may lag by several hours
- **Risk**: Some metrics may not be available for all communities (depends on community settings)

#### Authentication
- **OAuth flow**: Standard OAuth 2.0, but VK-specific implementation required
- **Token expiration**: Access tokens expire (typically 24 hours), refresh tokens required
- **Risk**: Token refresh failures require user to re-authenticate

### Telegram Bot API Constraints

**⚠️ VERIFICATION REQUIRED**: Confirm current limits at core.telegram.org/bots/api

#### Rate Limits (Confirmed from official documentation)
- **Private chats**: Maximum 1 message per second to the same user
- **Groups/Channels**: Maximum 20 messages per minute per group/channel
- **Global limit**: Maximum 30 messages per second across all chats
- **Risk**: Exceeding limits returns HTTP 429 (Too Many Requests) error
- **Mitigation**: Implement rate limiting queue with proper delays between messages

#### File Size Limits
- **Sending files**: Maximum 50 MB per file
- **Receiving files**: Maximum 20 MB per file
- **Photos**: Up to 10 MB (automatically compressed by Telegram)
- **Risk**: Larger files will fail to send
- **Mitigation**: Validate file sizes before scheduling, compress images if needed

#### Channel/Group Management
- **Bot permissions**: Bot must be added as administrator with "Post Messages" permission
- **Channel vs Group**: Different API methods for channels (`sendMessage`) vs groups
- **Risk**: Posts will fail if bot loses admin rights or permissions are revoked
- **Mitigation**: Validate bot permissions before scheduling, handle permission errors gracefully

#### Content Formatting
- **Markdown/HTML**: Supports MarkdownV2 and HTML formatting
- **Link previews**: Can be disabled per message
- **Media**: Supports photos, videos, documents, audio
- **Risk**: Formatting errors can cause message send failures
- **Mitigation**: Validate and sanitize formatting before sending

#### Analytics Data Access
- **Statistics**: Telegram Bot API does NOT provide built-in analytics
- **Workaround**: Must use Telegram Client API (MTProto) or third-party services
- **Risk**: Analytics for Telegram may be limited or require additional authentication
- **Mitigation**: For MVP, focus on basic metrics (subscriber count via `getChatMembersCount`)

#### Authentication
- **Bot token**: Single bot token per bot (no OAuth for users)
- **User authentication**: Not applicable (bots don't authenticate users)
- **Risk**: Bot token compromise allows full bot access
- **Mitigation**: Secure token storage, never expose in frontend code

---

## 3. Smallest Viable MVP Architecture

### Core Components

#### Frontend (React + Vite)
- **Pages**:
  - Login/Registration
  - Dashboard (analytics overview)
  - Communities (add/remove connections)
  - Calendar (scheduled posts view)
  - Post Editor (create/edit posts)
- **State management**: React Context API (no Redux for MVP)
- **UI library**: VKUI (if VK Mini App planned) or basic React components
- **API client**: Axios or fetch with error handling

#### Backend (FastAPI)
- **API structure**:
  - `/auth` - Authentication endpoints
  - `/users` - User management
  - `/communities` - Community connection management
  - `/analytics` - Analytics data endpoints
  - `/posts` - Post CRUD operations
  - `/scheduler` - Post scheduling and execution
- **Authentication**: JWT tokens
- **Database**: PostgreSQL (single database for MVP)
- **Background jobs**: Celery + Redis (for scheduled posts and analytics updates)

#### Database Schema (Minimal)
- **users**: id, email, password_hash, subscription_tier, created_at
- **communities**: id, user_id, platform (vk/telegram), external_id, access_token, name, created_at
- **posts**: id, user_id, content, scheduled_at, published_at, status (draft/scheduled/published/failed)
- **post_publications**: id, post_id, community_id, external_post_id, published_at, status
- **analytics_snapshots**: id, community_id, metric_name, metric_value, recorded_at

#### Integrations
- **VK API client**: Python library (vk-api or custom requests)
- **Telegram Bot API client**: python-telegram-bot or custom requests
- **Rate limiting**: Custom middleware or library (slowapi already in requirements)

#### Background Jobs (Celery)
- **Analytics fetcher**: Periodic task (every 6-12 hours) to fetch and store analytics
- **Post publisher**: Scheduled task to publish posts at specified times
- **Token refresh**: Periodic task to refresh VK access tokens

### Technical Decisions for MVP

1. **No real-time updates**: Polling-based UI updates (refresh button)
2. **Single database**: No read replicas or sharding
3. **Basic error handling**: Log errors, notify user via UI, manual retry
4. **No CDN**: Serve static assets from backend or simple frontend hosting
5. **Manual deployment**: No CI/CD pipeline in MVP (manual deployment process)
6. **Basic monitoring**: Application logs only (no APM tools)

---

## 4. Critical Risks and Mitigations

### Technical Risks
1. **API changes**: VK/Telegram may change APIs without notice
   - *Mitigation*: Version pinning, monitoring API status pages, graceful degradation

2. **Rate limit violations**: Exceeding API limits can block functionality
   - *Mitigation*: Conservative rate limiting, queue management, user warnings

3. **Token expiration**: VK tokens expire, requiring re-authentication
   - *Mitigation*: Automatic token refresh, clear error messages when refresh fails

4. **Post failures**: Network issues or API errors can cause post failures
   - *Mitigation*: Retry logic (3 attempts with exponential backoff), failure notifications

### Business Risks
1. **Platform policy changes**: VK/Telegram may restrict automated posting
   - *Mitigation*: Monitor platform announcements, implement compliance features

2. **User expectations**: MVP may not meet all user needs
   - *Mitigation*: Clear MVP scope communication, feedback collection mechanism

3. **Scalability**: Architecture may not scale beyond initial users
   - *Mitigation*: Design with scalability in mind, but optimize for MVP speed

---

## 5. MVP Success Criteria

### Functional Requirements
- ✅ User can register and log in
- ✅ User can connect at least one VK community and one Telegram channel
- ✅ User can view basic analytics (follower count, recent post engagement)
- ✅ User can create and schedule a post for future publication
- ✅ Scheduled post is automatically published at the correct time
- ✅ User can view published posts history

### Non-Functional Requirements
- ✅ Application handles API rate limits gracefully
- ✅ Failed operations show clear error messages
- ✅ Data refresh completes within 30 seconds for single community
- ✅ Post scheduling accuracy: ±1 minute tolerance

---

## Next Steps

**Before moving to Stage 2 (Architecture Design)**, please:
1. Review and confirm MVP scope boundaries
2. Verify VK API limitations in official documentation (vk.com/dev)
3. Verify Telegram Bot API limitations in official documentation (core.telegram.org/bots/api)
4. Confirm technical stack choices (FastAPI, React, PostgreSQL, Celery, Redis)
5. Identify any additional constraints or requirements

**Stage 2 will cover**:
- Detailed database schema design
- API endpoint specifications
- Frontend component structure
- Background job architecture
- Security considerations
- Deployment strategy
