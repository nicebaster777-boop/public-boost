/** Root App component. */

import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from './store/AuthContext';
import { router } from './router';

export function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}
