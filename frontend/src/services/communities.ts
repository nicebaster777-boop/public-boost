/** Communities API service. */

import { apiGet, apiPost, apiPatch } from './api';
import type { Community, CommunityCreate, CommunityUpdate } from '../types/community';
import type { ApiListResponse } from '../types/api';

export interface CommunitiesListParams {
  platform?: 'vk' | 'telegram';
  is_active?: boolean;
  page?: number;
  page_size?: number;
}

/**
 * Get list of communities.
 */
export async function getCommunities(
  params?: CommunitiesListParams,
): Promise<ApiListResponse<Community>> {
  const queryParams = new URLSearchParams();
  if (params?.platform) queryParams.append('platform', params.platform);
  if (params?.is_active !== undefined) queryParams.append('is_active', String(params.is_active));
  if (params?.page) queryParams.append('page', String(params.page));
  if (params?.page_size) queryParams.append('page_size', String(params.page_size));
  
  const query = queryParams.toString();
  return apiGet<ApiListResponse<Community>>(`/communities${query ? `?${query}` : ''}`);
}

/**
 * Get community by ID.
 */
export async function getCommunity(id: string): Promise<Community> {
  return apiGet<{ data: Community }>(`/communities/${id}`).then((r) => r.data);
}

/**
 * Create new community.
 */
export async function createCommunity(data: CommunityCreate): Promise<Community> {
  const response = await apiPost<{ data: Community }>('/communities', data);
  return response.data || (response as unknown as Community);
}

/**
 * Update community.
 */
export async function updateCommunity(
  id: string,
  data: CommunityUpdate,
): Promise<Community> {
  const response = await apiPatch<{ data: Community }>(`/communities/${id}`, data);
  return response.data || (response as unknown as Community);
}

/**
 * Disconnect community.
 */
export async function disconnectCommunity(id: string): Promise<void> {
  await apiPost(`/communities/${id}/disconnect`);
}

/**
 * Refresh community token.
 */
export async function refreshCommunityToken(id: string): Promise<void> {
  await apiPost(`/communities/${id}/refresh-token`);
}
