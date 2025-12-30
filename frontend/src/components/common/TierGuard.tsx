/** Tier guard component for feature gating. */

import { ReactNode } from 'react';
import { useAuth } from '../../store/AuthContext';

interface TierGuardProps {
  requiredTier: 'basic' | 'extended';
  children: ReactNode;
  fallback?: ReactNode;
}

export function TierGuard({ requiredTier, children, fallback }: TierGuardProps) {
  const { user } = useAuth();

  if (!user) {
    return fallback || null;
  }

  const hasAccess =
    requiredTier === 'basic' ||
    (requiredTier === 'extended' && user.subscription_tier === 'extended');

  if (!hasAccess) {
    return (
      fallback || (
        <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">
            Требуется расширенная подписка
          </h3>
          <p className="text-yellow-700">
            Эта функция доступна только для пользователей с расширенной подпиской.
          </p>
        </div>
      )
    );
  }

  return <>{children}</>;
}
