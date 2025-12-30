/** Calendar page (Extended tier only). */

import { TierGuard } from '../components/common/TierGuard';

export function CalendarPage() {
  return (
    <TierGuard requiredTier="extended">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Календарь</h1>
        <div className="bg-white p-8 rounded-lg shadow text-center">
          <p className="text-gray-600">Функция календаря будет реализована позже</p>
        </div>
      </div>
    </TierGuard>
  );
}
