/** Header component. */

import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../store/AuthContext';
import { useState } from 'react';

export function Header() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showTierMenu, setShowTierMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  const isActive = (path: string) => location.pathname === path;

  const getTierLabel = () => {
    return user?.subscription_tier === 'extended' ? 'Расширенный' : 'Базовый';
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-blue-600">S</span>
              <span className="text-xl font-bold text-gray-900">ocDash.</span>
            </Link>
            <nav className="flex space-x-1">
              <Link
                to="/"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/')
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                }`}
              >
                Дашборд
              </Link>
              {user?.subscription_tier === 'extended' && (
                <>
                  <Link
                    to="/calendar"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive('/calendar')
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                    }`}
                  >
                    Календарь
                  </Link>
                  <Link
                    to="/competitors"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive('/competitors')
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                    }`}
                  >
                    Конкуренты
                  </Link>
                </>
              )}
              <Link
                to="/settings"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/settings')
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                }`}
              >
                Настройки
              </Link>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            {/* Subscription Tier Dropdown */}
            <div className="relative">
              <button
                onClick={() => {
                  setShowTierMenu(!showTierMenu);
                  setShowUserMenu(false);
                }}
                className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
              >
                <span>{getTierLabel()}</span>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
              {showTierMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 text-sm text-gray-700 border-b">
                      Текущий план: {getTierLabel()}
                    </div>
                    <Link
                      to="/settings"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setShowTierMenu(false)}
                    >
                      Управление подпиской
                    </Link>
                  </div>
                </div>
              )}
            </div>
            {/* User Avatar Dropdown */}
            <div className="relative">
              <button
                onClick={() => {
                  setShowUserMenu(!showUserMenu);
                  setShowTierMenu(false);
                }}
                className="flex items-center space-x-2 focus:outline-none"
              >
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user?.email?.[0]?.toUpperCase() || 'U'}
                </div>
                <svg
                  className="w-4 h-4 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 text-sm text-gray-700 border-b">
                      {user?.email}
                    </div>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Выйти
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      {/* Close menus when clicking outside */}
      {(showUserMenu || showTierMenu) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setShowUserMenu(false);
            setShowTierMenu(false);
          }}
        />
      )}
    </header>
  );
}
