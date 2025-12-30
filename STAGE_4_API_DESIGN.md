# Stage 4: API Design

## Overview

This document defines the complete REST API specification for the MVP backend. The API follows RESTful principles and uses JSON for request/response payloads.

**Base URL**: `/api/v1`

**Authentication**: JWT Bearer tokens in `Authorization` header

**Content-Type**: `application/json`

**Design Principles:**
- RESTful resource-based URLs
- Consistent error response format
- Pagination for list endpoints
- Feature gating based on subscription tier
- Input validation on all endpoints
- Rate limiting per user

---

## Authentication

All endpoints except `/auth/*` require JWT authentication.

**Header Format:**
```
Authorization: Bearer <jwt_token>
```

**Token Expiration**: 24 hours
**Refresh Token**: Not implemented in MVP (user re-login required)

---

## Common Response Formats

### Success Response
```json
{
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... } // Optional additional error details
  }
}
```

### Pagination Response
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions (subscription tier)
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## Endpoints

### 1. Authentication Endpoints

#### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "timezone": "Europe/Moscow"
}
```

**Validation:**
- `email`: Valid email format, unique
- `password`: Min 8 characters, at least one letter and one number
- `timezone`: Valid IANA timezone identifier (optional, defaults to UTC)

**Response:** `201 Created`
```json
{
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "subscription_tier": "basic",
      "timezone": "Europe/Moscow",
      "created_at": "2024-01-15T10:00:00Z"
    },
    "token": "jwt_token_string"
  }
}
```

**Errors:**
- `400` - Validation error (invalid email, weak password)
- `409` - Email already exists

---

#### POST /auth/login

Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "subscription_tier": "basic",
      "timezone": "Europe/Moscow"
    },
    "token": "jwt_token_string"
  }
}
```

**Errors:**
- `401` - Invalid credentials
- `400` - Validation error

---

#### POST /auth/logout

Logout user (invalidate token on client side).

**Request:** None (token in header)

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

**Note**: In MVP, logout is client-side only (token deletion). Server-side token blacklist is postponed.

---

### 2. User Endpoints

#### GET /users/me

Get current user profile.

**Request:** None (authenticated)

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "subscription_tier": "basic",
    "timezone": "Europe/Moscow",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
}
```

---

#### PATCH /users/me

Update current user profile.

**Request:**
```json
{
  "timezone": "Europe/Moscow"
}
```

**Validation:**
- `timezone`: Valid IANA timezone identifier (optional)

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "subscription_tier": "basic",
    "timezone": "Europe/Moscow",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Note**: Email and subscription_tier cannot be changed via API (admin-only operations in MVP).

---

### 3. Communities Endpoints

#### GET /communities

Get list of user's communities.

**Query Parameters:**
- `platform` (optional): Filter by platform (`vk`, `telegram`)
- `is_active` (optional): Filter by active status (`true`, `false`)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "platform": "vk",
      "external_id": "123456789",
      "name": "My VK Group",
      "is_active": true,
      "last_sync_at": "2024-01-15T10:00:00Z",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 5,
    "total_pages": 1
  }
}
```

**Note**: Tokens are never returned in list/detail responses (security).

---

#### GET /communities/{community_id}

Get community details.

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "platform": "vk",
    "external_id": "123456789",
    "name": "My VK Group",
    "is_active": true,
    "token_expires_at": "2024-01-16T10:00:00Z",
    "last_sync_at": "2024-01-15T10:00:00Z",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
}
```

**Errors:**
- `404` - Community not found or not owned by user

---

#### POST /communities

Connect a new community.

**Request:**
```json
{
  "platform": "vk",
  "external_id": "123456789",
  "name": "My VK Group",
  "access_token": "vk_access_token_string", // Required for VK
  "refresh_token": "vk_refresh_token_string", // Optional, VK only
  "bot_token": "telegram_bot_token_string" // Required for Telegram
}
```

**Validation:**
- `platform`: Required, must be `vk` or `telegram`
- `external_id`: Required, valid platform ID
- `name`: Required, max 255 characters
- `access_token`: Required for VK, must not be provided for Telegram
- `refresh_token`: Optional, VK only, must not be provided for Telegram
- `bot_token`: Required for Telegram, must not be provided for VK

**Response:** `201 Created`
```json
{
  "data": {
    "id": "uuid",
    "platform": "vk",
    "external_id": "123456789",
    "name": "My VK Group",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

**Errors:**
- `400` - Validation error
- `403` - Subscription tier doesn't allow community connections (if limit reached)
- `409` - Community already connected

**Note**: Backend validates token and user permissions with external API before storing.

---

#### POST /communities/{community_id}/disconnect

Disconnect (soft delete) a community.

**Request:** None

**Response:** `200 OK`
```json
{
  "message": "Community disconnected successfully"
}
```

**Errors:**
- `404` - Community not found

**Note**: Soft delete sets `deleted_at`. Scheduled posts targeting this community will fail.

---

#### PATCH /communities/{community_id}

Update community details (name only in MVP).

**Request:**
```json
{
  "name": "Updated Community Name"
}
```

**Validation:**
- `name`: Optional, max 255 characters

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "platform": "vk",
    "external_id": "123456789",
    "name": "Updated Community Name",
    "is_active": true,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Errors:**
- `400` - Validation error
- `404` - Community not found

**Note**: Tokens cannot be updated via this endpoint (use refresh-token endpoint for VK).

---

#### POST /communities/{community_id}/refresh-token

Manually trigger token refresh (VK only).

**Request:** None

**Response:** `200 OK`
```json
{
  "message": "Token refresh initiated"
}
```

**Note**: Enqueues background task to refresh token. Frontend should poll for status.

---

### 4. Posts Endpoints

#### GET /posts

Get list of user's posts.

**Query Parameters:**
- `status` (optional): Filter by status (`draft`, `scheduled`, `publishing`, `published`, `failed`, `partially_published`)
- `community_id` (optional): Filter by target community
- `scheduled_from` (optional): Filter posts scheduled from date (ISO 8601)
- `scheduled_to` (optional): Filter posts scheduled to date (ISO 8601)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "content_text": "Post content here",
      "image_url": "https://example.com/image.jpg",
      "scheduled_at": "2024-01-20T12:00:00Z",
      "status": "scheduled",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z",
      "publications": [
        {
          "id": "uuid",
          "community_id": "uuid",
          "community_name": "My VK Group",
          "status": "pending"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 50,
    "total_pages": 3
  }
}
```

**Feature Gating**: Requires `extended` subscription tier.

---

#### GET /posts/{post_id}

Get post details.

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "content_text": "Post content here",
    "image_url": "https://example.com/image.jpg",
    "scheduled_at": "2024-01-20T12:00:00Z",
    "status": "scheduled",
    "error_message": null,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "publications": [
      {
        "id": "uuid",
        "community_id": "uuid",
        "community_name": "My VK Group",
        "platform": "vk",
        "status": "pending",
        "external_post_id": null,
        "published_at": null,
        "error_message": null
      }
    ]
  }
}
```

**Errors:**
- `404` - Post not found or not owned by user

**Feature Gating**: Requires `extended` subscription tier.

---

#### POST /posts

Create a new post.

**Request:**
```json
{
  "content_text": "Post content here",
  "image_url": "https://example.com/image.jpg", // Optional, use /upload/image first
  "scheduled_at": "2024-01-20T12:00:00Z", // Optional, if not provided = draft
  "community_ids": ["uuid1", "uuid2"] // Required if scheduled_at provided
}
```

**Validation:**
- `content_text`: Required, max 10,000 characters
- `image_url`: Optional, must be valid URL from /upload/image endpoint
- `scheduled_at`: Optional, must be in future, max 30 days ahead, ISO 8601 format
- `community_ids`: Required if `scheduled_at` provided, must be array with at least 1 community ID, all must be user's active communities (not soft-deleted)

**Response:** `201 Created`
```json
{
  "data": {
    "id": "uuid",
    "content_text": "Post content here",
    "image_url": "https://example.com/image.jpg",
    "scheduled_at": "2024-01-20T12:00:00Z",
    "status": "scheduled",
    "created_at": "2024-01-15T10:00:00Z",
    "publications": [
      {
        "id": "uuid",
        "community_id": "uuid1",
        "status": "pending"
      }
    ]
  }
}
```

**Errors:**
- `400` - Validation error
- `403` - Subscription tier doesn't allow autoposting (`basic` tier)
- `404` - One or more communities not found

**Feature Gating**: Requires `extended` subscription tier.

**Note**: 
- If `scheduled_at` not provided, post is created as `draft` (no task enqueued)
- If `scheduled_at` provided, post is `scheduled` and task is enqueued in Redis + database
- `scheduled_at` is stored in UTC, but user provides time in their timezone (converted on backend)
- All timestamps in API responses are in ISO 8601 format (UTC)

---

#### PATCH /posts/{post_id}

Update a post (only if status is `draft` or `scheduled`).

**Request:**
```json
{
  "content_text": "Updated content",
  "image_url": "https://example.com/new-image.jpg", // Optional, use /upload/image first
  "scheduled_at": "2024-01-21T14:00:00Z", // Optional
  "community_ids": ["uuid1", "uuid3"] // Optional, replaces existing targets if provided
}
```

**Validation:**
- Same as POST /posts
- Post must be in `draft` or `scheduled` status

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "content_text": "Updated content",
    "scheduled_at": "2024-01-21T14:00:00Z",
    "status": "scheduled",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Errors:**
- `400` - Validation error or post cannot be edited (already publishing/published)
- `404` - Post not found

**Feature Gating**: Requires `extended` subscription tier.

**Note**: 
- Updating `scheduled_at` or `community_ids` cancels existing scheduled task and creates new one
- If updating removes some communities, their PostPublication records are soft-deleted
- If updating adds communities, new PostPublication records are created with status 'pending'

---

#### DELETE /posts/{post_id}

Delete a post (only if status is `draft` or `scheduled`).

**Request:** None

**Response:** `200 OK`
```json
{
  "message": "Post deleted successfully"
}
```

**Errors:**
- `400` - Post cannot be deleted (already publishing/published)
- `404` - Post not found

**Feature Gating**: Requires `extended` subscription tier.

**Note**: Cancels scheduled task if post is scheduled.

---

#### POST /posts/{post_id}/publish-now

Publish a post immediately (bypasses schedule).

**Request:** None

**Response:** `200 OK`
```json
{
  "message": "Post publishing initiated",
  "data": {
    "post_id": "uuid",
    "status": "publishing"
  }
}
```

**Errors:**
- `400` - Post cannot be published (wrong status, no target communities)
- `404` - Post not found

**Feature Gating**: Requires `extended` subscription tier.

**Note**: Enqueues immediate publishing task. Post status changes to `publishing`.

---

#### POST /posts/{post_id}/retry

Retry a failed post.

**Request:** None

**Response:** `200 OK`
```json
{
  "message": "Post retry initiated",
  "data": {
    "post_id": "uuid",
    "status": "publishing"
  }
}
```

**Errors:**
- `400` - Post cannot be retried (not in failed status)
- `404` - Post not found

**Feature Gating**: Requires `extended` subscription tier.

---

### 5. Analytics Endpoints

#### GET /analytics/dashboard

Get dashboard analytics for all user's communities.

**Query Parameters:**
- `date_from` (optional): Start date for metrics (ISO 8601, default: 30 days ago)
- `date_to` (optional): End date for metrics (ISO 8601, default: now)

**Response:** `200 OK`
```json
{
  "data": {
    "account_health": {
      "score": 7,
      "max_score": 10,
      "metrics": {
        "total_reach": 124500,
        "new_subscribers": 850,
        "engagement_rate": 6.8
      }
    },
    "communities": [
      {
        "id": "uuid",
        "name": "My VK Group",
        "platform": "vk",
        "current_followers": 12500,
        "follower_growth": 850,
        "engagement_rate": 6.8,
        "last_sync_at": "2024-01-15T10:00:00Z"
      }
    ],
    "subscriber_dynamics": {
      "period": "7d",
      "data": [
        {
          "date": "2024-01-09",
          "vk": 12000,
          "telegram": 4500
        }
      ]
    }
  }
}
```

**Note**: 
- Aggregates data from latest analytics snapshots. Returns empty data if no snapshots available.
- `account_health.score` calculated from multiple factors (token validity, sync status, engagement trends)
- `subscriber_dynamics` aggregates follower counts per platform over time period
- Available for both `basic` and `extended` tiers

---

#### GET /analytics/communities/{community_id}

Get detailed analytics for a specific community.

**Query Parameters:**
- `date_from` (optional): Start date (ISO 8601, default: 30 days ago)
- `date_to` (optional): End date (ISO 8601, default: now)
- `metric` (optional): Filter by metric name (e.g., `follower_count`, `engagement_rate`)

**Response:** `200 OK`
```json
{
  "data": {
    "community": {
      "id": "uuid",
      "name": "My VK Group",
      "platform": "vk"
    },
    "metrics": [
      {
        "metric_name": "follower_count",
        "values": [
          {
            "value": 12500,
            "recorded_at": "2024-01-15T10:00:00Z"
          }
        ],
        "trend": "up",
        "change_percent": 7.2
      }
    ],
    "period": {
      "from": "2024-01-01T00:00:00Z",
      "to": "2024-01-15T23:59:59Z"
    }
  }
}
```

**Errors:**
- `404` - Community not found

---

#### POST /analytics/communities/{community_id}/refresh

Manually trigger analytics refresh for a community.

**Request:** None

**Response:** `200 OK`
```json
{
  "message": "Analytics refresh initiated",
  "data": {
    "community_id": "uuid",
    "status": "pending"
  }
}
```

**Note**: 
- Enqueues background task to fetch analytics from external API
- Frontend should poll `/analytics/communities/{community_id}` to check for updated `last_sync_at`
- Task typically completes within 30 seconds for single community
- Available for both `basic` and `extended` tiers

---

#### GET /analytics/recommendations

Get AI-generated recommendations (if available).

**Response:** `200 OK`
```json
{
  "data": {
    "recommendations": [
      {
        "id": "uuid",
        "type": "schedule_video",
        "priority": "high",
        "title": "Запланируйте видео-пост в ВК в среду",
        "description": "Видео-посты показывают лучшую вовлеченность по средам",
        "action": {
          "type": "create_post",
          "suggested_time": "2024-01-17T14:00:00Z",
          "platform": "vk"
        }
      },
      {
        "id": "uuid",
        "type": "increase_activity",
        "priority": "medium",
        "title": "Повысьте активность в Telegram утром",
        "description": "Утренние посты получают на 15% больше просмотров",
        "action": {
          "type": "schedule_morning_posts",
          "platform": "telegram"
        }
      }
    ]
  }
}
```

**Note**: 
- Recommendations are generated based on analytics data (last 30 days)
- Returns empty array if insufficient data (< 7 days of snapshots)
- Recommendations include: best posting times, content type suggestions, activity optimization
- Available for both `basic` and `extended` tiers

---

### 6. Calendar Endpoints

#### GET /calendar

Get calendar view of scheduled posts.

**Query Parameters:**
- `month` (optional): Month number (1-12, default: current month)
- `year` (optional): Year (default: current year)
- `community_id` (optional): Filter by community

**Response:** `200 OK`
```json
{
  "data": {
    "month": 1,
    "year": 2024,
    "posts": [
      {
        "id": "uuid",
        "content_text": "Post content",
        "scheduled_at": "2024-01-20T12:00:00Z",
        "status": "scheduled",
        "communities": [
          {
            "id": "uuid",
            "name": "My VK Group",
            "platform": "vk"
          }
        ]
      }
    ]
  }
}
```

**Feature Gating**: Requires `extended` subscription tier.

---

### 7. File Upload Endpoints

#### POST /upload/image

Upload an image for post.

**Request:** Multipart form data
- `file`: Image file (JPEG, PNG, max 5 MB)

**Response:** `200 OK`
```json
{
  "data": {
    "url": "https://example.com/uploads/image.jpg",
    "storage_path": "/uploads/image.jpg",
    "size": 1024000,
    "mime_type": "image/jpeg"
  }
}
```

**Errors:**
- `400` - Invalid file (wrong format, too large, validation error)
- `413` - File too large (exceeds 5 MB)

**Note**: 
- Image is stored permanently (not temporary)
- Use returned `url` in `image_url` field when creating/updating posts
- Images are cleaned up if not used in posts within 24 hours (background job)
- Feature gating: Requires `extended` subscription tier

---

## Error Codes

### Authentication Errors
- `AUTH_INVALID_CREDENTIALS` - Invalid email or password
- `AUTH_TOKEN_EXPIRED` - JWT token expired
- `AUTH_TOKEN_INVALID` - Invalid JWT token format
- `AUTH_REQUIRED` - Authentication required

### Validation Errors
- `VALIDATION_ERROR` - General validation error (details in `details` field)
- `VALIDATION_EMAIL_INVALID` - Invalid email format
- `VALIDATION_PASSWORD_WEAK` - Password doesn't meet requirements
- `VALIDATION_REQUIRED_FIELD` - Required field missing

### Resource Errors
- `RESOURCE_NOT_FOUND` - Resource not found
- `RESOURCE_ALREADY_EXISTS` - Resource already exists (e.g., duplicate community)
- `RESOURCE_OWNERSHIP_ERROR` - User doesn't own the resource

### Business Logic Errors
- `POST_CANNOT_EDIT` - Post cannot be edited (wrong status)
- `POST_CANNOT_DELETE` - Post cannot be deleted (wrong status)
- `POST_CANNOT_PUBLISH` - Post cannot be published (no communities, wrong status)
- `COMMUNITY_TOKEN_EXPIRED` - Community token expired, refresh required
- `COMMUNITY_INVALID_PERMISSIONS` - User doesn't have required permissions on platform

### Subscription Errors
- `SUBSCRIPTION_TIER_INSUFFICIENT` - Subscription tier doesn't allow this feature
- `SUBSCRIPTION_LIMIT_REACHED` - Subscription limit reached (e.g., max communities)

### External API Errors
- `EXTERNAL_API_ERROR` - Error from VK/Telegram API
- `EXTERNAL_API_RATE_LIMIT` - Rate limit exceeded on external API
- `EXTERNAL_API_UNAVAILABLE` - External API temporarily unavailable

### System Errors
- `INTERNAL_ERROR` - Internal server error
- `SERVICE_UNAVAILABLE` - Service temporarily unavailable

---

## Rate Limiting

**Limits:**
- Authentication endpoints: 5 requests per minute per IP
- All other endpoints: 100 requests per minute per user

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**Response on limit exceeded:** `429 Too Many Requests`
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later."
  }
}
```

---

## Feature Gating

### Basic Tier
- ✅ View analytics
- ✅ Connect communities
- ❌ Create/schedule posts
- ❌ Calendar view

### Extended Tier
- ✅ All Basic features
- ✅ Create/schedule posts
- ✅ Calendar view
- ✅ Post management

**Implementation**: Check `user.subscription_tier` on relevant endpoints, return `403 Forbidden` if insufficient.

---

## Webhooks / Real-time Updates

**Not implemented in MVP**. Frontend should poll for updates:
- Post status: Poll `/posts/{post_id}` every 5-10 seconds when status is `publishing`
- Analytics refresh: Poll `/analytics/communities/{community_id}` after triggering refresh

---

## Versioning

**Current Version**: `v1`

**URL Format**: `/api/v1/...`

**Future Versions**: `/api/v2/...` (backward compatibility maintained)

---

## Timezone Handling

**Storage**: All timestamps stored in UTC in database

**API Input**: 
- User provides timestamps in their timezone (from `user.timezone`)
- Backend converts to UTC before storage
- Example: User in `Europe/Moscow` (UTC+3) schedules post for `2024-01-20T15:00:00` → stored as `2024-01-20T12:00:00Z`

**API Output**: 
- All timestamps returned in ISO 8601 format (UTC)
- Frontend converts to user's timezone for display
- Example: `2024-01-20T12:00:00Z` → displayed as `2024-01-20T15:00:00` for `Europe/Moscow`

**User Timezone**: 
- Set during registration or updated via `PATCH /users/me`
- Stored as IANA timezone identifier (e.g., `Europe/Moscow`, `America/New_York`)
- Default: `UTC` if not provided

---

## Data Consistency Notes

### Post Status Transitions
- `draft` → `scheduled` (when `scheduled_at` set)
- `scheduled` → `publishing` (when worker starts)
- `publishing` → `published` (all PostPublications succeed)
- `publishing` → `failed` (all PostPublications fail after retries)
- `publishing` → `partially_published` (some succeed, some fail)

### PostPublication Status Transitions
- `pending` → `publishing` (when worker starts publishing to this community)
- `publishing` → `success` (publication succeeds, `external_post_id` set)
- `publishing` → `failed` (publication fails after retries, `error_message` set)

### Community Soft Delete
- Setting `deleted_at` marks community as deleted
- Active queries filter by `deleted_at IS NULL`
- Scheduled posts targeting deleted community will fail with appropriate error

---

## Что мне нужно сделать (пошагово)

1. **Просмотреть API спецификацию**: Прочитать `STAGE_4_API_DESIGN.md` и проверить все endpoints

2. **Проверить соответствие интерфейсу**: Убедиться, что все endpoints покрывают функциональность из скриншота (дашборд, календарь, создание постов, рекомендации)

3. **Проверить валидацию**: Подтвердить, что все валидационные правила корректны

4. **Проверить feature gating**: Убедиться, что разделение Basic/Extended tier логично

5. **Проверить error handling**: Подтвердить, что все error codes покрывают возможные сценарии

6. **После подтверждения**: Одобрить переход к Stage 5 (Frontend Design) или к реализации (Stage 6)

