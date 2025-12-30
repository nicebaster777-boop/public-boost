/** Dashboard page. */

import { useEffect, useState } from 'react';
import { useAuth } from '../store/AuthContext';
import { getCommunities } from '../services/communities';
import type { Community } from '../types/community';

export function DashboardPage() {
  const { user } = useAuth();
  const [communities, setCommunities] = useState<Community[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCommunities();
  }, []);

  const loadCommunities = async () => {
    try {
      setLoading(true);
      const response = await getCommunities({ is_active: true });
      setCommunities(response.data || []);
    } catch (err) {
      setError('Не удалось загрузить сообщества');
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
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Дашборд</h1>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Подписка
          </h3>
          <p className="text-2xl font-bold text-blue-600">
            {user?.subscription_tier === 'extended' ? 'Расширенная' : 'Базовая'}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Сообщества
          </h3>
          <p className="text-2xl font-bold text-gray-900">
            {communities.length}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Часовой пояс
          </h3>
          <p className="text-sm text-gray-600">{user?.timezone}</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Подключенные сообщества
        </h2>
        {communities.length === 0 ? (
          <p className="text-gray-600">Нет подключенных сообществ</p>
        ) : (
          <div className="space-y-4">
            {communities.map((community) => (
              <div
                key={community.id}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {community.name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {community.platform === 'vk' ? 'VK' : 'Telegram'}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded ${
                      community.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {community.is_active ? 'Активно' : 'Неактивно'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
