/** Settings page. */

import { useState, FormEvent } from 'react';
import { useAuth } from '../store/AuthContext';
import { Button } from '../components/common/Button';
import { Select } from '../components/common/Select';
import { apiPatch } from '../services/api';
import { ApiError } from '../services/api';
import { getTimezones } from '../utils/timezones';

export function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [timezone, setTimezone] = useState(user?.timezone || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const timezones = getTimezones();

  if (!user) {
    return null;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);

    try {
      await apiPatch('/users/me', { timezone });
      await refreshUser();
      setSuccess(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('Не удалось обновить настройки');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Настройки</h1>

      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Профиль
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <p className="text-gray-900">{user.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Подписка
            </label>
            <p className="text-gray-900">
              {user.subscription_tier === 'extended' ? 'Расширенная' : 'Базовая'}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Часовой пояс
        </h2>
        <form onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
              Настройки успешно обновлены
            </div>
          )}
          <Select
            label="Часовой пояс"
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            options={timezones}
            required
          />
          <div className="mt-4">
            <Button type="submit" loading={loading}>
              Сохранить
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
