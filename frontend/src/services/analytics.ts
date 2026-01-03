/** Analytics API service. */

import { apiGet, apiPost } from './api';
import type { DashboardData, Recommendation, AnalyticsSnapshot } from '../types/analytics';
import type { ApiListResponse } from '../types/api';

/**
 * Get dashboard data.
 */
export async function getDashboardData(dateFrom?: string, dateTo?: string): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (dateFrom) params.append('date_from', dateFrom);
  if (dateTo) params.append('date_to', dateTo);
  const query = params.toString();
  return apiGet<DashboardData>(`/analytics/dashboard${query ? `?${query}` : ''}`);
}

/**
 * Get recommendations.
 */
export async function getRecommendations(): Promise<Recommendation[]> {
  const response = await apiGet<{ recommendations: Recommendation[] }>('/analytics/recommendations');
  return response.recommendations || [];
}

/**
 * Get analytics snapshots for a community.
 */
export async function getCommunityAnalytics(
  communityId: string,
  params?: { from_date?: string; to_date?: string },
): Promise<ApiListResponse<AnalyticsSnapshot>> {
  const queryParams = new URLSearchParams();
  if (params?.from_date) queryParams.append('from_date', params.from_date);
  if (params?.to_date) queryParams.append('to_date', params.to_date);
  
  const query = queryParams.toString();
  return apiGet<ApiListResponse<AnalyticsSnapshot>>(
    `/analytics/communities/${communityId}/snapshots${query ? `?${query}` : ''}`,
  );
}

/**
 * Refresh analytics for a community.
 */
export async function refreshCommunityAnalytics(communityId: string): Promise<void> {
  await apiPost(`/analytics/communities/${communityId}/refresh`);
}
