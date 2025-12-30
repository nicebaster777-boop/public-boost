# Stage 5: Frontend Design

## Overview

This document defines the complete frontend architecture for the MVP, including component structure, routing, state management, and API integration. The frontend is built with React 19, TypeScript, React Router 7, and Vite.

**Tech Stack:**
- React 19.2.0
- TypeScript 5.9
- React Router 7.10.1
- Vite 7.2.2
- No UI library in MVP (custom components, can add VKUI later)

**Design Principles:**
- Component-based architecture
- Type-safe with TypeScript
- Responsive design (desktop-first, mobile-friendly)
- Optimistic updates where appropriate
- Clear loading and error states
- Feature gating based on subscription tier

---

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/          # Common components (Button, Input, etc.)
│   │   ├── layout/          # Layout components (Header, Sidebar, etc.)
│   │   ├── analytics/       # Analytics-specific components
│   │   ├── posts/           # Post-related components
│   │   └── calendar/        # Calendar components
│   ├── pages/               # Page components (routes)
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── CalendarPage.tsx
│   │   ├── CommunitiesPage.tsx
│   │   └── SettingsPage.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useCommunities.ts
│   │   ├── usePosts.ts
│   │   └── useAnalytics.ts
│   ├── services/            # API service layer
│   │   ├── api.ts           # Base API client
│   │   ├── auth.ts          # Auth API
│   │   ├── communities.ts   # Communities API
│   │   ├── posts.ts         # Posts API
│   │   └── analytics.ts     # Analytics API
│   ├── store/               # State management (Context API)
│   │   ├── AuthContext.tsx
│   │   ├── CommunitiesContext.tsx
│   │   └── AppContext.tsx
│   ├── types/               # TypeScript type definitions
│   │   ├── api.ts
│   │   ├── user.ts
│   │   ├── community.ts
│   │   ├── post.ts
│   │   └── analytics.ts
│   ├── utils/               # Utility functions
│   │   ├── date.ts          # Date/timezone utilities
│   │   ├── validation.ts    # Form validation
│   │   └── constants.ts     # App constants
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── router.tsx           # Route configuration
├── public/                  # Static assets
├── package.json
└── tsconfig.json
```

---

## Routing Structure

### Public Routes (Unauthenticated)
- `/login` - Login page
- `/register` - Registration page

### Protected Routes (Authenticated)
- `/` or `/dashboard` - Dashboard (analytics overview)
- `/calendar` - Calendar view (extended tier only)
- `/communities` - Communities management
- `/posts` - Posts list and management (extended tier only)
- `/settings` - User settings

### Route Guards
- `ProtectedRoute` component checks authentication
- `TierGuard` component checks subscription tier for extended features
- Redirects to `/login` if not authenticated
- Shows upgrade message if tier insufficient

---

## Page Components

### 1. LoginPage

**Route:** `/login`

**Features:**
- Email and password input
- Form validation (client-side)
- Error message display
- "Remember me" checkbox (stores token in localStorage)
- Link to registration page
- Redirects to dashboard on success

**State:**
- `email: string`
- `password: string`
- `rememberMe: boolean`
- `error: string | null`
- `loading: boolean`

**API Calls:**
- `POST /auth/login`

---

### 2. RegisterPage

**Route:** `/register`

**Features:**
- Email, password, timezone input
- Password strength indicator
- Form validation
- Error message display
- Link to login page
- Redirects to dashboard on success

**State:**
- `email: string`
- `password: string`
- `confirmPassword: string`
- `timezone: string` (default: browser timezone)
- `error: string | null`
- `loading: boolean`

**API Calls:**
- `POST /auth/register`

---

### 3. DashboardPage

**Route:** `/` or `/dashboard`

**Features:**
- Account health widget (gauge chart)
- Subscriber dynamics chart (line graph)
- Top-3 recommendations list
- Communities overview cards
- Manual refresh button for analytics
- Feature gating: Available for both tiers

**Components Used:**
- `AccountHealthWidget`
- `SubscriberDynamicsChart`
- `RecommendationsList`
- `CommunitiesOverview`

**State:**
- `dashboardData: DashboardData | null`
- `loading: boolean`
- `error: string | null`
- `lastRefresh: Date | null`

**API Calls:**
- `GET /analytics/dashboard`
- `GET /analytics/recommendations`
- `POST /analytics/communities/{id}/refresh` (manual refresh)

**Polling:**
- Auto-refresh every 5 minutes (if user is on page)

---

### 4. CalendarPage

**Route:** `/calendar`

**Features:**
- Monthly calendar view
- Scheduled posts displayed on dates
- Click date to view/create post
- Filter by community
- Quick actions bar (create post, add competitor - if available)
- Feature gating: Extended tier only

**Components Used:**
- `CalendarGrid`
- `PostCard` (mini version)
- `QuickActionsBar`
- `PostModal` (create/edit)

**State:**
- `currentMonth: number`
- `currentYear: number`
- `selectedDate: Date | null`
- `posts: Post[]`
- `filteredCommunityId: string | null`
- `showPostModal: boolean`

**API Calls:**
- `GET /calendar?month={month}&year={year}`
- `GET /posts?status=scheduled&scheduled_from={date}&scheduled_to={date}`

---

### 5. CommunitiesPage

**Route:** `/communities`

**Features:**
- List of connected communities
- Add new community button
- Platform filter (VK, Telegram, All)
- Community cards with status, metrics preview
- Connect/disconnect actions
- Token expiration warnings
- Feature gating: Available for both tiers

**Components Used:**
- `CommunityCard`
- `ConnectCommunityModal`
- `CommunityDetailsModal`

**State:**
- `communities: Community[]`
- `filterPlatform: 'all' | 'vk' | 'telegram'`
- `showConnectModal: boolean`
- `selectedCommunity: Community | null`

**API Calls:**
- `GET /communities`
- `POST /communities`
- `POST /communities/{id}/disconnect`
- `POST /communities/{id}/refresh-token`

---

### 6. PostsPage (Extended Tier Only)

**Route:** `/posts`

**Features:**
- List of all posts (draft, scheduled, published, failed)
- Status filter
- Community filter
- Date range filter
- Create post button
- Edit/delete actions (for draft/scheduled)
- Retry action (for failed)
- Publish now action (for scheduled)
- Feature gating: Extended tier only

**Components Used:**
- `PostList`
- `PostCard`
- `PostFilters`
- `PostModal` (create/edit)

**State:**
- `posts: Post[]`
- `statusFilter: PostStatus | 'all'`
- `communityFilter: string | null`
- `dateFrom: Date | null`
- `dateTo: Date | null`
- `showPostModal: boolean`
- `editingPost: Post | null`

**API Calls:**
- `GET /posts?status={status}&community_id={id}&scheduled_from={date}&scheduled_to={date}`
- `POST /posts`
- `PATCH /posts/{id}`
- `DELETE /posts/{id}`
- `POST /posts/{id}/publish-now`
- `POST /posts/{id}/retry`

---

### 7. SettingsPage

**Route:** `/settings`

**Features:**
- User profile display
- Timezone selector
- Subscription tier display (read-only, admin changes)
- Logout button
- Feature gating: Available for both tiers

**State:**
- `user: User | null`
- `timezone: string`
- `loading: boolean`

**API Calls:**
- `GET /users/me`
- `PATCH /users/me`

---

## Component Library

### Common Components

#### Button
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger' | 'outline';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}
```

#### Input
```typescript
interface InputProps {
  type: 'text' | 'email' | 'password' | 'number' | 'date' | 'time';
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
}
```

#### Modal
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}
```

#### LoadingSpinner
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}
```

#### ErrorMessage
```typescript
interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
}
```

### Layout Components

#### Header
- Logo "SocDash."
- Navigation links (Dashboard, Calendar, Communities, Settings)
- Subscription tier badge (Basic/Extended)
- User profile dropdown (logout)

#### ProtectedRoute
- Wraps protected routes
- Checks authentication
- Redirects to login if not authenticated

#### TierGuard
- Wraps extended-tier features
- Checks subscription tier
- Shows upgrade message if insufficient

### Analytics Components

#### AccountHealthWidget
- Semi-circular gauge chart (0-10 scale)
- Color segments (red, orange, yellow, green)
- Metrics display: Total Reach, New Subscribers, Engagement Rate
- Uses SVG or canvas for gauge

#### SubscriberDynamicsChart
- Line chart showing follower growth over time
- Two lines: VK (blue) and Telegram (red)
- X-axis: Days of week or dates
- Y-axis: Subscriber count
- Uses chart library (Chart.js or Recharts)

#### RecommendationsList
- List of 3 recommendation cards
- Each card: icon, title, description, action button
- Types: schedule_video, increase_activity, analyze_competitors

#### CommunitiesOverview
- Grid of community cards
- Each card: name, platform icon, follower count, engagement rate
- Click to view details

### Post Components

#### PostCard
- Post content preview
- Scheduled time
- Status badge
- Target communities
- Actions (edit, delete, publish now, retry)

#### PostModal
- Create/edit post form
- Platform selection (checkboxes)
- Text area with character counter
- Image upload/preview
- Date/time picker
- Community selection (multi-select)
- Action buttons (Schedule, Publish Now, Cancel)

#### PostFilters
- Status dropdown
- Community dropdown
- Date range picker
- Clear filters button

### Calendar Components

#### CalendarGrid
- Monthly grid view
- Days of week header
- Date cells with scheduled posts
- Navigation (prev/next month)
- Today highlight
- Click date to view/create post

#### QuickActionsBar
- "Создать пост" button (Create post)
- "Добавить конкурента" button (disabled in MVP)
- "Сгенерировать отчет" button (disabled in MVP)

---

## State Management

### Context API Structure

#### AuthContext
```typescript
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, timezone: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}
```

**Storage:**
- Token: localStorage (if "remember me") or sessionStorage
- User: Context state (refreshed on login)

#### CommunitiesContext
```typescript
interface CommunitiesContextType {
  communities: Community[];
  loading: boolean;
  error: string | null;
  fetchCommunities: () => Promise<void>;
  addCommunity: (community: CreateCommunityData) => Promise<void>;
  removeCommunity: (id: string) => Promise<void>;
  refreshCommunity: (id: string) => Promise<void>;
}
```

**Caching:**
- Communities cached in context
- Refetch on mount and after mutations
- Optimistic updates for add/remove

#### AppContext (Global)
```typescript
interface AppContextType {
  subscriptionTier: 'basic' | 'extended';
  timezone: string;
  setTimezone: (tz: string) => void;
  featureEnabled: (feature: string) => boolean;
}
```

---

## API Integration

### Base API Client

**File:** `src/services/api.ts`

```typescript
class ApiClient {
  private baseURL: string;
  private token: string | null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('token') || sessionStorage.getItem('token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
      sessionStorage.removeItem('token');
    }
  }

  async request<T>(
    method: string,
    endpoint: string,
    data?: unknown
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config: RequestInit = {
      method,
      headers,
    };

    if (data) {
      config.body = JSON.stringify(data);
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.error.code, error.error.message, error.error.details);
    }

    return response.json();
  }

  get<T>(endpoint: string): Promise<T> {
    return this.request<T>('GET', endpoint);
  }

  post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>('PATCH', endpoint, data);
  }

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint);
  }
}
```

### Service Modules

**File:** `src/services/auth.ts`
- `login(email, password)`
- `register(email, password, timezone)`
- `logout()`
- `getCurrentUser()`

**File:** `src/services/communities.ts`
- `getCommunities(filters?)`
- `getCommunity(id)`
- `createCommunity(data)`
- `updateCommunity(id, data)`
- `disconnectCommunity(id)`
- `refreshToken(id)`

**File:** `src/services/posts.ts`
- `getPosts(filters?)`
- `getPost(id)`
- `createPost(data)`
- `updatePost(id, data)`
- `deletePost(id)`
- `publishNow(id)`
- `retryPost(id)`

**File:** `src/services/analytics.ts`
- `getDashboard(dateFrom?, dateTo?)`
- `getCommunityAnalytics(id, dateFrom?, dateTo?)`
- `refreshAnalytics(id)`
- `getRecommendations()`

**File:** `src/services/upload.ts`
- `uploadImage(file)`

### Error Handling

**File:** `src/utils/errors.ts`

```typescript
class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const handleApiError = (error: unknown): string => {
  if (error instanceof ApiError) {
    switch (error.code) {
      case 'AUTH_INVALID_CREDENTIALS':
        return 'Неверный email или пароль';
      case 'AUTH_TOKEN_EXPIRED':
        return 'Сессия истекла. Пожалуйста, войдите снова.';
      case 'SUBSCRIPTION_TIER_INSUFFICIENT':
        return 'Эта функция доступна только в расширенном тарифе';
      case 'VALIDATION_ERROR':
        return error.message || 'Ошибка валидации';
      case 'RATE_LIMIT_EXCEEDED':
        return 'Слишком много запросов. Попробуйте позже.';
      default:
        return error.message || 'Произошла ошибка';
    }
  }
  return 'Неизвестная ошибка';
};
```

---

## Custom Hooks

### useAuth
```typescript
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

### useApi
```typescript
const useApi = <T,>(
  apiCall: () => Promise<T>,
  dependencies: unknown[] = []
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    apiCall()
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(handleApiError(err));
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, dependencies);

  return { data, loading, error, refetch: () => apiCall() };
};
```

### useCommunities
```typescript
const useCommunities = () => {
  const context = useContext(CommunitiesContext);
  if (!context) throw new Error('useCommunities must be used within CommunitiesProvider');
  return context;
};
```

### usePosts
```typescript
const usePosts = (filters?: PostFilters) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPosts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await postsService.getPosts(filters);
      setPosts(data.data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  return { posts, loading, error, refetch: fetchPosts };
};
```

### useAnalytics
```typescript
const useAnalytics = (communityId?: string) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const data = await analyticsService.getDashboard();
      setDashboardData(data.data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return { dashboardData, loading, error, refetch: fetchDashboard };
};
```

---

## TypeScript Types

### User Types

**File:** `src/types/user.ts`

```typescript
export type SubscriptionTier = 'basic' | 'extended';

export interface User {
  id: string;
  email: string;
  subscription_tier: SubscriptionTier;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  timezone: string;
}
```

### Community Types

**File:** `src/types/community.ts`

```typescript
export type Platform = 'vk' | 'telegram';

export interface Community {
  id: string;
  platform: Platform;
  external_id: string;
  name: string;
  is_active: boolean;
  token_expires_at: string | null;
  last_sync_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateCommunityRequest {
  platform: Platform;
  external_id: string;
  name: string;
  access_token?: string; // VK only
  refresh_token?: string; // VK only
  bot_token?: string; // Telegram only
}
```

### Post Types

**File:** `src/types/post.ts`

```typescript
export type PostStatus = 
  | 'draft' 
  | 'scheduled' 
  | 'publishing' 
  | 'published' 
  | 'failed' 
  | 'partially_published';

export type PublicationStatus = 'pending' | 'publishing' | 'success' | 'failed';

export interface PostPublication {
  id: string;
  community_id: string;
  community_name: string;
  platform: Platform;
  status: PublicationStatus;
  external_post_id: string | null;
  published_at: string | null;
  error_message: string | null;
}

export interface Post {
  id: string;
  content_text: string;
  image_url: string | null;
  scheduled_at: string | null;
  status: PostStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  publications: PostPublication[];
}

export interface CreatePostRequest {
  content_text: string;
  image_url?: string;
  scheduled_at?: string; // ISO 8601
  community_ids: string[];
}

export interface PostFilters {
  status?: PostStatus;
  community_id?: string;
  scheduled_from?: string;
  scheduled_to?: string;
  page?: number;
  page_size?: number;
}
```

### Analytics Types

**File:** `src/types/analytics.ts`

```typescript
export interface AccountHealth {
  score: number;
  max_score: number;
  metrics: {
    total_reach: number;
    new_subscribers: number;
    engagement_rate: number;
  };
}

export interface CommunityMetrics {
  id: string;
  name: string;
  platform: Platform;
  current_followers: number;
  follower_growth: number;
  engagement_rate: number;
  last_sync_at: string;
}

export interface SubscriberDynamics {
  period: string;
  data: Array<{
    date: string;
    vk: number;
    telegram: number;
  }>;
}

export interface DashboardData {
  account_health: AccountHealth;
  communities: CommunityMetrics[];
  subscriber_dynamics: SubscriberDynamics;
}

export interface Recommendation {
  id: string;
  type: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  action: {
    type: string;
    suggested_time?: string;
    platform?: Platform;
  };
}
```

---

## Utility Functions

### Date/Timezone Utilities

**File:** `src/utils/date.ts`

```typescript
export const formatDate = (date: string | Date, timezone: string): string => {
  // Convert UTC to user timezone and format
};

export const formatDateTime = (date: string | Date, timezone: string): string => {
  // Format date and time in user timezone
};

export const toUTC = (date: Date, timezone: string): Date => {
  // Convert user timezone to UTC
};

export const fromUTC = (date: Date, timezone: string): Date => {
  // Convert UTC to user timezone
};
```

### Validation Utilities

**File:** `src/utils/validation.ts`

```typescript
export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

export const validatePassword = (password: string): {
  valid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];
  if (password.length < 8) errors.push('Минимум 8 символов');
  if (!/[a-zA-Z]/.test(password)) errors.push('Должна содержать буквы');
  if (!/[0-9]/.test(password)) errors.push('Должна содержать цифры');
  return { valid: errors.length === 0, errors };
};

export const validatePostContent = (content: string): {
  valid: boolean;
  error?: string;
} => {
  if (content.length === 0) {
    return { valid: false, error: 'Текст поста обязателен' };
  }
  if (content.length > 10000) {
    return { valid: false, error: 'Максимум 10000 символов' };
  }
  return { valid: true };
};
```

---

## Styling Approach

### CSS Modules (Recommended)

**Structure:**
```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   └── Button.module.css
```

**Example:**
```css
/* Button.module.css */
.button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.primary {
  background-color: #007bff;
  color: white;
}

.secondary {
  background-color: #6c757d;
  color: white;
}
```

### Global Styles

**File:** `src/index.css`

```css
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --background: #f8f9fa;
  --text: #212529;
  --border: #dee2e6;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background-color: var(--background);
  color: var(--text);
}
```

---

## Feature Gating Implementation

### TierGuard Component

```typescript
interface TierGuardProps {
  requiredTier: 'basic' | 'extended';
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const TierGuard: React.FC<TierGuardProps> = ({ 
  requiredTier, 
  children, 
  fallback 
}) => {
  const { user } = useAuth();
  
  if (!user) return null;
  
  const hasAccess = 
    requiredTier === 'basic' || 
    (requiredTier === 'extended' && user.subscription_tier === 'extended');
  
  if (!hasAccess) {
    return fallback || <UpgradeMessage />;
  }
  
  return <>{children}</>;
};
```

### Usage in Routes

```typescript
<Route
  path="/calendar"
  element={
    <TierGuard requiredTier="extended">
      <CalendarPage />
    </TierGuard>
  }
/>
```

---

## Loading and Error States

### Loading States
- Full-page spinner for initial page load
- Inline spinners for button actions
- Skeleton loaders for data lists
- Progress indicators for file uploads

### Error States
- Toast notifications for API errors
- Inline error messages for form validation
- Error boundaries for component errors
- Retry buttons for failed operations

---

## Responsive Design

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Mobile Considerations
- Hamburger menu for navigation
- Stacked layout for dashboard widgets
- Full-screen modals
- Touch-friendly button sizes (min 44x44px)

---

## Performance Optimizations

### Code Splitting
- Route-based code splitting (React.lazy)
- Component lazy loading for heavy components

### Memoization
- React.memo for expensive components
- useMemo for computed values
- useCallback for event handlers

### API Optimization
- Request debouncing for search/filters
- Pagination for large lists
- Caching in Context API
- Optimistic updates where safe

---

## Testing Strategy (Post-MVP)

### Unit Tests
- Utility functions
- Custom hooks
- Component logic

### Integration Tests
- API service layer
- Form submissions
- Navigation flows

### E2E Tests (Post-MVP)
- User registration/login
- Create and schedule post
- View analytics

---

## Что мне нужно сделать (пошагово)

1. **Просмотреть Frontend Design**: Прочитать `STAGE_5_FRONTEND_DESIGN.md` и проверить структуру компонентов

2. **Проверить соответствие интерфейсу**: Убедиться, что все компоненты из скриншота покрыты (дашборд, календарь, форма поста, рекомендации)

3. **Проверить соответствие API**: Убедиться, что все API endpoints из Stage 4 используются в компонентах

4. **Проверить feature gating**: Подтвердить, что разделение Basic/Extended tier реализовано корректно

5. **После подтверждения**: Начать реализацию или перейти к финальной проверке всех стадий перед реализацией
