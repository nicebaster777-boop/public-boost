/** Forgot password page. */

import { useState, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { apiPost } from '../services/api';
import { ApiError } from '../services/api';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);

    try {
      await apiPost('/auth/forgot-password', { email });
      setSuccess(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('Произошла ошибка при отправке запроса');
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
            Восстановление пароля
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Введите ваш email, и мы отправим инструкции по восстановлению пароля
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              Инструкции по восстановлению пароля отправлены на ваш email. Пожалуйста, проверьте почту.
            </div>
          )}
          {!success && (
            <>
              <div className="space-y-4">
                <Input
                  type="email"
                  label="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>
              <div>
                <Button type="submit" className="w-full" loading={loading}>
                  Отправить инструкции
                </Button>
              </div>
            </>
          )}
          <div className="text-center space-y-2">
            <Link
              to="/login"
              className="text-blue-600 hover:text-blue-500 text-sm block"
            >
              Вернуться к входу
            </Link>
            <Link
              to="/register"
              className="text-blue-600 hover:text-blue-500 text-sm block"
            >
              Нет аккаунта? Зарегистрироваться
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
