import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/useAuth'
import { authApi } from '../api/auth'
import { getApiErrorData } from '../utils/apiError'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({
    email_or_phone: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleGoogleLogin = async () => {
    const { client_id: clientId } = await authApi.getSocialConfig('google').catch(() => ({ client_id: '' }))
    if (!clientId || clientId === 'your-google-client-id-here') {
      setError('Вход через Google временно недоступен: OAuth client ID не настроен.')
      return
    }
    const redirectUri = encodeURIComponent(window.location.origin + '/google-callback')
    const scope = encodeURIComponent('profile email')
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=token&scope=${scope}`

    const popup = window.open(authUrl, 'googleAuth', 'width=500,height=600')

    // Слушаем сообщение от popup
    const messageHandler = (event: MessageEvent) => {
      if (event.origin === window.location.origin && event.data.type === 'google_token') {
        window.removeEventListener('message', messageHandler)

        const accessToken = event.data.token
        if (accessToken) {
          authApi.socialLogin('google', { access_token: accessToken })
            .then((response) => {
              console.log('Google login response:', response)
              login(
                {
                  access: response.access,
                  refresh: response.refresh,
                },
                response.user,
              )
              navigate('/')
              // Закрываем popup после успешного входа
              if (popup && !popup.closed) {
                popup.close()
              }
            })
            .catch((err) => {
              console.error('Google login error:', err)
              setError('Ошибка входа через Google')
            })
        }
      }
    }

    window.addEventListener('message', messageHandler)
  }

  const handleVkLogin = async () => {
    const { client_id: clientId } = await authApi.getSocialConfig('vk').catch(() => ({ client_id: '' }))
    if (!clientId || clientId === 'your-vk-client-id-here') {
      setError('Вход через VK временно недоступен: OAuth client ID не настроен.')
      return
    }

    const redirectUri = encodeURIComponent(`${window.location.origin}/google-callback?provider=vk`)
    const authUrl = `https://oauth.vk.com/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=token&scope=email`
    const popup = window.open(authUrl, 'vkAuth', 'width=500,height=600')
    const messageHandler = (event: MessageEvent) => {
      if (event.origin !== window.location.origin || event.data.type !== 'vk_token') return
      window.removeEventListener('message', messageHandler)
      authApi.socialLogin('vk', { access_token: event.data.token })
        .then((response) => {
          login({ access: response.access, refresh: response.refresh }, response.user)
          navigate('/')
          popup?.close()
        })
        .catch(() => setError('Не удалось войти через VK. Проверьте настройки OAuth.'))
    }
    window.addEventListener('message', messageHandler)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Преобразуем email_or_phone в contact и определяем тип
      const contact = formData.email_or_phone.trim()
      const contactType = contact.includes('@') ? 'email' : 'phone'
      
      const response = await authApi.login({
        contact,
        contact_type: contactType as 'email' | 'phone',
        password: formData.password,
      })
      
      // Парсим ответ от бэкенда (tokens содержит access и refresh)
      login({
        access: response.tokens.access,
        refresh: response.tokens.refresh,
      }, response.user)
      navigate('/')
    } catch (err: unknown) {
      // Обработка различных типов ошибок
      const errorData = getApiErrorData(err)
      if (errorData && typeof errorData !== 'string') {
        
        // Если есть сообщение об ошибке в поле contact
        if (errorData.contact && Array.isArray(errorData.contact)) {
          setError(String(errorData.contact[0]))
        } 
        // Если есть сообщение об ошибке в поле password
        else if (errorData.password && Array.isArray(errorData.password)) {
          setError(String(errorData.password[0]))
        }
        // Если есть общее сообщение detail
        else if (errorData.detail) {
          setError(errorData.detail)
        } 
        // Если это другая ошибка
        else {
          setError('Ошибка входа. Проверьте email/телефон и пароль.')
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
            Вход в аккаунт
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Или{' '}
            <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
              зарегистрируйтесь
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email_or_phone" className="sr-only">
                Email или телефон
              </label>
              <input
                id="email_or_phone"
                name="email_or_phone"
                type="text"
                required
                className="appearance-none rounded-none rounded-t-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Email или телефон"
                value={formData.email_or_phone}
                onChange={(e) => setFormData({ ...formData, email_or_phone: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-none rounded-b-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Пароль"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm">
              <Link
                to="/password-reset"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Забыли пароль?
              </Link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Вход...' : 'Войти'}
            </button>
          </div>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">Или войдите через</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={handleGoogleLogin}
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
              >
                Google
              </button>
              <button
                type="button"
                onClick={handleVkLogin}
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
              >
                ВКонтакте
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
