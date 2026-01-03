/** Subscriber Dynamics Chart - Line chart showing follower growth. */

import { useState } from 'react';
import type { SubscriberDynamics } from '../../types/analytics';

interface SubscriberDynamicsChartProps {
  data: SubscriberDynamics;
}

export function SubscriberDynamicsChart({ data }: SubscriberDynamicsChartProps) {
  const [showVK, setShowVK] = useState(true);
  const [showTelegram, setShowTelegram] = useState(true);
  if (!data.data || data.data.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Динамика подписчиков</h3>
        <p className="text-gray-600 text-center py-8">Нет данных для отображения</p>
      </div>
    );
  }

  const maxValue = Math.max(
    ...data.data.map((d) => Math.max(d.vk || 0, d.telegram || 0))
  );
  const chartHeight = 200;
  const chartWidth = 100;
  const padding = 20;

  const points = data.data.map((d, index) => {
    const x = padding + (index / (data.data.length - 1 || 1)) * (chartWidth - padding * 2);
    const vkY = chartHeight - padding - ((d.vk || 0) / maxValue) * (chartHeight - padding * 2);
    const telegramY =
      chartHeight - padding - ((d.telegram || 0) / maxValue) * (chartHeight - padding * 2);
    return { x, vkY, telegramY, date: d.date };
  });

  const vkPath =
    'M ' +
    points.map((p) => `${p.x},${p.vkY}`).join(' L ') +
    (points.length > 0 ? ` L ${points[points.length - 1].x},${chartHeight - padding} L ${points[0].x},${chartHeight - padding} Z` : '');

  const telegramPath =
    'M ' +
    points.map((p) => `${p.x},${p.telegramY}`).join(' L ') +
    (points.length > 0 ? ` L ${points[points.length - 1].x},${chartHeight - padding} L ${points[0].x},${chartHeight - padding} Z` : '');

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Динамика подписчиков</h3>
        {/* Legend with checkboxes */}
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showVK}
              onChange={(e) => setShowVK(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-blue-500 rounded"></div>
              <span className="text-sm text-gray-700">ВК</span>
            </div>
          </label>
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showTelegram}
              onChange={(e) => setShowTelegram(e.target.checked)}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span className="text-sm text-gray-700">Telep</span>
            </div>
          </label>
        </div>
      </div>
      <div className="relative" style={{ height: `${chartHeight}px` }}>
        <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth + padding * 2} ${chartHeight}`}>
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const y = padding + ratio * (chartHeight - padding * 2);
            return (
              <line
                key={ratio}
                x1={padding}
                y1={y}
                x2={chartWidth + padding}
                y2={y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            );
          })}
          {/* VK line (blue) */}
          {points.length > 1 && showVK && (
            <path
              d={vkPath.split(' Z')[0]}
              fill="none"
              stroke="#3b82f6"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}
          {/* Telegram line (red) */}
          {points.length > 1 && showTelegram && (
            <path
              d={telegramPath.split(' Z')[0]}
              fill="none"
              stroke="#ef4444"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}
          {/* Points */}
          {points.map((p, i) => (
            <g key={i}>
              {showVK && <circle cx={p.x} cy={p.vkY} r="3" fill="#3b82f6" />}
              {showTelegram && <circle cx={p.x} cy={p.telegramY} r="3" fill="#ef4444" />}
            </g>
          ))}
        </svg>
        {/* X-axis labels */}
        <div className="flex justify-between mt-2 text-xs text-gray-600">
          {points.map((p, i) => (
            <span key={i} className="truncate" style={{ maxWidth: `${100 / points.length}%` }}>
              {new Date(p.date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
