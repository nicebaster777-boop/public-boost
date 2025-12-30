/** User types. */

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
  timezone?: string;
}

export interface UserUpdate {
  timezone?: string;
  subscription_tier?: SubscriptionTier;
}
