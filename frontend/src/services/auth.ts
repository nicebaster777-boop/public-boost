/** Authentication API service. */

import { apiPost, apiGet } from './api';
import type { LoginRequest, RegisterRequest, User } from '../types/user';
import { STORAGE_KEYS } from '../utils/constants';

export interface LoginResponse {
  token: string;
  user: User;
}

export interface RegisterResponse extends LoginResponse {}

/**
 * Login user.
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await apiPost<LoginResponse>('/auth/login', credentials);
  localStorage.setItem(STORAGE_KEYS.TOKEN, response.token);
  localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user));
  return response;
}

/**
 * Register new user.
 */
export async function register(data: RegisterRequest): Promise<RegisterResponse> {
  const response = await apiPost<LoginResponse>('/auth/register', data);
  // Register also returns token and user, so we can store them
  localStorage.setItem(STORAGE_KEYS.TOKEN, response.token);
  localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user));
  return response;
}

/**
 * Logout user.
 */
export async function logout(): Promise<void> {
  try {
    await apiPost('/auth/logout');
  } catch {
    // Ignore errors on logout
  } finally {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
  }
}

/**
 * Get current user.
 */
export async function getCurrentUser(): Promise<User> {
  return apiGet<User>('/users/me');
}
