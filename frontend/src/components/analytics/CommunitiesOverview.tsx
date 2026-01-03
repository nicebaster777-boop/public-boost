/** Communities Overview - Grid of community cards. */

import type { CommunityMetrics } from '../../types/analytics';

interface CommunitiesOverviewProps {
  communities: CommunityMetrics[];
}

export function CommunitiesOverview({ communities }: CommunitiesOverviewProps) {
  if (communities.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Сообщества</h3>
        <p className="text-gray-600 text-center py-4">Нет подключенных сообществ</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Сообщества</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {communities.map((community) => (
          <div
            key={community.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{community.name}</h4>
                <p className="text-sm text-gray-600">
                  {community.platform === 'vk' ? 'VK' : 'Telegram'}
                </p>
              </div>
              <span className="text-2xl">
                {community.platform === 'vk' ? '🔵' : '💬'}
              </span>
            </div>
            <div className="space-y-2 mt-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Подписчики:</span>
                <span className="font-semibold">{community.current_followers.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Прирост:</span>
                <span
                  className={`font-semibold ${
                    community.follower_growth >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {community.follower_growth >= 0 ? '+' : ''}
                  {community.follower_growth.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Вовлеченность:</span>
                <span className="font-semibold">{community.engagement_rate.toFixed(2)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
