/** Account Health Widget - Semi-circular gauge chart. */

interface AccountHealthWidgetProps {
  score: number;
  maxScore: number;
  metrics: {
    total_reach?: number;
    new_subscribers?: number;
    engagement_rate?: number;
  };
}

export function AccountHealthWidget({ score, maxScore, metrics }: AccountHealthWidgetProps) {
  const percentage = (score / maxScore) * 100;
  
  // Color based on score
  let color = '#ef4444'; // red
  if (percentage >= 75) color = '#22c55e'; // green
  else if (percentage >= 50) color = '#eab308'; // yellow
  else if (percentage >= 25) color = '#f97316'; // orange

  // SVG semi-circle gauge
  const radius = 80;
  const circumference = Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Здоровье аккаунтов</h3>
      <div className="flex items-center justify-center mb-6">
        <div className="relative" style={{ width: '200px', height: '120px' }}>
          <svg
            width="200"
            height="120"
            viewBox="0 0 200 120"
            className="transform -rotate-90"
          >
            {/* Background arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
              strokeLinecap="round"
            />
            {/* Score arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke={color}
              strokeWidth="20"
              strokeLinecap="round"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              style={{ transition: 'stroke-dashoffset 0.5s ease' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center transform rotate-90">
              <div className="text-4xl font-bold" style={{ color }}>
                {score}
              </div>
              <div className="text-sm text-gray-600">из {maxScore}</div>
            </div>
          </div>
        </div>
      </div>
      <div className="space-y-2">
        {metrics.total_reach !== undefined && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Общий охват:</span>
            <span className="font-semibold">{metrics.total_reach.toLocaleString()}</span>
          </div>
        )}
        {metrics.new_subscribers !== undefined && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Новые подписчики:</span>
            <span className="font-semibold text-green-600">
              +{metrics.new_subscribers.toLocaleString()}
            </span>
          </div>
        )}
        {metrics.engagement_rate !== undefined && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Вовлеченность:</span>
            <span className="font-semibold">{metrics.engagement_rate.toFixed(2)}%</span>
          </div>
        )}
      </div>
    </div>
  );
}
