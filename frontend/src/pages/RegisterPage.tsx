/** Register page. */

import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register as apiRegister, login as apiLogin } from '../services/auth';
import { useAuth } from '../store/AuthContext';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Select } from '../components/common/Select';
import { ApiError } from '../services/api';
import { getTimezones, getUserTimezone } from '../utils/timezones';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [timezone, setTimezone] = useState(getUserTimezone());
  const timezones = getTimezones();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (password.length < 8) {
      setError('Пароль должен содержать минимум 8 символов');
      return;
    }

    setLoading(true);

    try {
      // Register returns token and user directly
      const registerResponse = await apiRegister({ email, password, timezone });
      login(registerResponse.user, registerResponse.token);
      navigate('/');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('Произошла ошибка при регистрации');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Регистрация
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <Input
              type="email"
              label="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
            <Input
              type="password"
              label="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <Input
              type="password"
              label="Подтвердите пароль"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <Select
              label="Часовой пояс"
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              options={timezones}
              required
            />
          </div>
          <div>
            <Button type="submit" className="w-full" loading={loading}>
              Зарегистрироваться
            </Button>
          </div>
          <div className="text-center space-y-2">
            <Link
              to="/login"
              className="text-blue-600 hover:text-blue-500 text-sm block"
            >
              Уже есть аккаунт? Войти
            </Link>
            <Link
              to="/forgot-password"
              className="text-blue-600 hover:text-blue-500 text-sm block"
            >
              Забыли пароль?
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
