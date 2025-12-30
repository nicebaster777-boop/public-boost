/** Application constants. */

// Use /api for proxy in dev, or full URL in production
// Proxy will rewrite /api/* to /api/v1/* and forward to backend
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const STORAGE_KEYS = {
  TOKEN: 'auth_token',
  USER: 'user_data',
} as const;

export const SUBSCRIPTION_TIERS = {
  BASIC: 'basic',
  EXTENDED: 'extended',
} as const;
