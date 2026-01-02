/** Application constants. */

// Use /api/v1 for proxy - nginx forwards /api to backend which expects /api/v1
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const STORAGE_KEYS = {
  TOKEN: 'auth_token',
  USER: 'user_data',
} as const;

export const SUBSCRIPTION_TIERS = {
  BASIC: 'basic',
  EXTENDED: 'extended',
} as const;
