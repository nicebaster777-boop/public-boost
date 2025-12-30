/** Analytics types. */

export interface AnalyticsSnapshot {
  id: string;
  community_id: string;
  snapshot_date: string;
  follower_count: number;
  engagement_rate: number;
  metric_metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface DashboardData {
  total_communities: number;
  total_followers: number;
  average_engagement_rate: number;
  account_health_score: number;
}

export interface Recommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}
