/** Recommendations List - Top 3 recommendations. */

import type { Recommendation } from '../../types/analytics';
import { Button } from '../common/Button';

interface RecommendationsListProps {
  recommendations: Recommendation[];
}

const getRecommendationIcon = (type: string) => {
  switch (type) {
    case 'schedule_video':
      return '📹';
    case 'increase_activity':
      return '📈';
    case 'analyze_competitors':
      return '🔍';
    default:
      return '💡';
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'border-red-200 bg-red-50';
    case 'medium':
      return 'border-yellow-200 bg-yellow-50';
    case 'low':
      return 'border-blue-200 bg-blue-50';
    default:
      return 'border-gray-200 bg-gray-50';
  }
};

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  if (recommendations.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Рекомендации</h3>
        <p className="text-gray-600 text-center py-4">Нет рекомендаций</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Рекомендации</h3>
      <div className="space-y-4">
        {recommendations.slice(0, 3).map((rec) => (
          <div
            key={rec.id}
            className={`border rounded-lg p-4 ${getPriorityColor(rec.priority)}`}
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{getRecommendationIcon(rec.type)}</span>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">{rec.title}</h4>
                <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                <Button
                  variant="outline"
                  size="small"
                  onClick={() => {
                    // TODO: Implement action
                    console.log('Action:', rec.action);
                  }}
                >
                  Применить
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
