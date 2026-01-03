/** Router configuration. */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Layout } from './components/layout/Layout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { CommunitiesPage } from './pages/CommunitiesPage';
import { CalendarPage } from './pages/CalendarPage';
import { PostsPage } from './pages/PostsPage';
import { SettingsPage } from './pages/SettingsPage';
import { CompetitorsPage } from './pages/CompetitorsPage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPasswordPage />,
  },
  {
    path: '/reset-password',
    element: <ResetPasswordPage />,
  },
  {
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: '/',
        element: <DashboardPage />,
      },
      {
        path: '/communities',
        element: <CommunitiesPage />,
      },
      {
        path: '/calendar',
        element: <CalendarPage />,
      },
      {
        path: '/competitors',
        element: <CompetitorsPage />,
      },
      {
        path: '/posts',
        element: <PostsPage />,
      },
      {
        path: '/settings',
        element: <SettingsPage />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
