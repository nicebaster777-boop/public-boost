/** Dashboard page. */

import { useEffect, useState } from 'react';
import { useAuth } from '../store/AuthContext';
import { getDashboardData, getRecommendations } from '../services/analytics';
import type { DashboardData } from '../types/analytics';
import type { Recommendation } from '../types/analytics';
import { AccountHealthWidget } from '../components/analytics/AccountHealthWidget';
import { SubscriberDynamicsChart } from '../components/analytics/SubscriberDynamicsChart';
import { RecommendationsList } from '../components/analytics/RecommendationsList';
import { CommunitiesOverview } from '../components/analytics/CommunitiesOverview';
import { Button } from '../components/common/Button';

export function DashboardPage() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashboard, recs] = await Promise.all([
        getDashboardData(),
        getRecommendations(),
      ]);
      setDashboardData(dashboard);
      setRecommendations(recs);
      setLastRefresh(new Date());
    } catch (err) {
      setError('Не удалось загрузить данные дашборда');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Дашборд</h1>
        <Button onClick={loadDashboard} variant="outline" size="small">
          Обновить
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {lastRefresh && (
        <p className="text-sm text-gray-600 mb-6">
          Последнее обновление: {lastRefresh.toLocaleTimeString('ru-RU')}
        </p>
      )}

      {dashboardData && (
        <>
          {/* Top row: Account Health and Subscriber Dynamics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <AccountHealthWidget
              score={dashboardData.account_health.score}
              maxScore={dashboardData.account_health.max_score}
              metrics={dashboardData.account_health.metrics}
            />
            <SubscriberDynamicsChart data={dashboardData.subscriber_dynamics} />
          </div>

          {/* Recommendations */}
          <div className="mb-6">
            <RecommendationsList recommendations={recommendations} />
          </div>

          {/* Communities Overview */}
          <div className="mb-6">
            <CommunitiesOverview communities={dashboardData.communities} />
          </div>
        </>
      )}
    </div>
  );
}
