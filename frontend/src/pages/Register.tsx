import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authApi } from '../api/auth'

export default function Register() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    password: '',
    password2: '',
    agree_personal_data: false,
    agree_privacy_policy: false,
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.agree_personal_data || !formData.agree_privacy_policy) {
      setError('Необходимо согласие с условиями')
      return
    }

    if (formData.password !== formData.password2) {
      setError('Пароли не совпадают')
      return
    }

    setIsLoading(true)

    try {
      const response = await authApi.register({
        email: formData.email,
        phone: formData.phone || undefined,
        password: formData.password,
        password2: formData.password2,
      })
      
      // Парсим ответ от бэкенда (tokens содержит access и refresh)
      login({
        access: response.tokens.access,
        refresh: response.tokens.refresh,
      }, response.user)
      navigate('/')
    } catch (err: any) {
      // Обработка различных типов ошибок
      if (err.response?.data) {
        const errorData = err.response.data
        
        // Если это объект с полями ошибок (как от DRF)
        if (typeof errorData === 'object' && !errorData.detail) {
          const firstError = Object.values(errorData)[0]
          if (Array.isArray(firstError)) {
            setError(firstError[0])
          } else {
            setError(firstError as string)
          }
        } else {
          setError(errorData.detail || 'Ошибка регистрации')
        }
      } else {
        setError('Ошибка сети. Убедитесь, что сервер запущен.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Регистрация
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Уже есть аккаунт?{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Войдите
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="your@email.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Телефон (опционально)
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="+7XXXXXXXXXX"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Пароль *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                minLength={8}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Минимум 8 символов"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="password2" className="block text-sm font-medium text-gray-700">
                Подтвердите пароль *
              </label>
              <input
                id="password2"
                name="password2"
                type="password"
                required
                minLength={8}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Повторите пароль"
                value={formData.password2}
                onChange={(e) => setFormData({ ...formData, password2: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-3">
            <label className="flex items-start">
              <input
                type="checkbox"
                required
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
                checked={formData.agree_personal_data}
                onChange={(e) =>
                  setFormData({ ...formData, agree_personal_data: e.target.checked })
                }
              />
              <span className="ml-2 text-sm text-gray-600">
                Я согласен на{' '}
                <Link to="/legal/personal-data" className="text-blue-600 hover:underline">
                  обработку персональных данных
                </Link>
                *
              </span>
            </label>
            <label className="flex items-start">
              <input
                type="checkbox"
                required
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
                checked={formData.agree_privacy_policy}
                onChange={(e) =>
                  setFormData({ ...formData, agree_privacy_policy: e.target.checked })
                }
              />
              <span className="ml-2 text-sm text-gray-600">
                Я ознакомлен с{' '}
                <Link to="/legal/privacy-policy" className="text-blue-600 hover:underline">
                  политикой обработки персональных данных
                </Link>
                *
              </span>
            </label>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
