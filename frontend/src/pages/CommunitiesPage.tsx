/** Communities page. */

import { useEffect, useState } from 'react';
import { getCommunities, disconnectCommunity } from '../services/communities';
import type { Community } from '../types/community';
import { Button } from '../components/common/Button';
import { ApiError } from '../services/api';

export function CommunitiesPage() {
  const [communities, setCommunities] = useState<Community[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterPlatform, setFilterPlatform] = useState<'all' | 'vk' | 'telegram'>('all');

  useEffect(() => {
    loadCommunities();
  }, [filterPlatform]);

  const loadCommunities = async () => {
    try {
      setLoading(true);
      const params = filterPlatform !== 'all' ? { platform: filterPlatform } : {};
      const response = await getCommunities(params);
      setCommunities(response.data || []);
    } catch (err) {
      setError('Не удалось загрузить сообщества');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async (id: string) => {
    if (!confirm('Вы уверены, что хотите отключить это сообщество?')) {
      return;
    }

    try {
      await disconnectCommunity(id);
      await loadCommunities();
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Ошибка: ${err.detail}`);
      } else {
        alert('Не удалось отключить сообщество');
      }
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
        <h1 className="text-3xl font-bold text-gray-900">Сообщества</h1>
        <Button onClick={() => alert('Функция подключения сообщества будет реализована позже')}>
          Подключить сообщество
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-4">
        <div className="flex space-x-2">
          <Button
            variant={filterPlatform === 'all' ? 'primary' : 'outline'}
            size="small"
            onClick={() => setFilterPlatform('all')}
          >
            Все
          </Button>
          <Button
            variant={filterPlatform === 'vk' ? 'primary' : 'outline'}
            size="small"
            onClick={() => setFilterPlatform('vk')}
          >
            VK
          </Button>
          <Button
            variant={filterPlatform === 'telegram' ? 'primary' : 'outline'}
            size="small"
            onClick={() => setFilterPlatform('telegram')}
          >
            Telegram
          </Button>
        </div>
      </div>

      {communities.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow text-center">
          <p className="text-gray-600 mb-4">Нет подключенных сообществ</p>
          <Button onClick={() => alert('Функция подключения сообщества будет реализована позже')}>
            Подключить первое сообщество
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {communities.map((community) => (
            <div key={community.id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
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
              <div className="flex space-x-2">
                <Button
                  variant="danger"
                  size="small"
                  onClick={() => handleDisconnect(community.id)}
                >
                  Отключить
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
