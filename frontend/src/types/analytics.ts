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

export interface AccountHealth {
  score: number;
  max_score: number;
  metrics: {
    total_reach?: number;
    new_subscribers?: number;
    engagement_rate?: number;
  };
}

export interface CommunityMetrics {
  id: string;
  name: string;
  platform: 'vk' | 'telegram';
  current_followers: number;
  follower_growth: number;
  engagement_rate: number;
  last_sync_at: string | null;
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
    platform?: 'vk' | 'telegram';
  };
}
