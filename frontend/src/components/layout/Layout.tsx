/** Layout component for protected routes. */

import { Outlet } from 'react-router-dom';
import { Header } from './Header';

export function Layout() {
  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50">
        <Outlet />
      </main>
    </>
  );
}
