import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authApi } from '../api/auth'

export default function PasswordReset() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await authApi.passwordReset({ email_or_phone: email })
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отправки ссылки')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className='min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8'>
        <div className='max-w-md w-full space-y-8'>
          <div className='text-center'>
            <div className='mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100'>
              <svg
                className='h-6 w-6 text-green-600'
                fill='none'
                viewBox='0 0 24 24'
                stroke='currentColor'
              >
                <path
                  strokeLinecap='round'
                  strokeLinejoin='round'
                  strokeWidth={2}
                  d='M5 13l4 4L19 7'
                />
              </svg>
            </div>
            <h2 className='mt-6 text-3xl font-extrabold text-gray-900'>
              Ссылка отправлена
            </h2>
            <p className='mt-2 text-sm text-gray-600'>
              Проверьте вашу почту для получения инструкции по сбросу пароля
            </p>
          </div>
          <div className='text-center'>
            <Link
              to='/login'
              className='font-medium text-blue-600 hover:text-blue-500'
            >
              Вернуться к входу
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className='min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8'>
      <div className='max-w-md w-full space-y-8'>
        <div>
          <h2 className='mt-6 text-center text-3xl font-extrabold text-gray-900'>
            Сброс пароля
          </h2>
          <p className='mt-2 text-center text-sm text-gray-600'>
            Введите email или телефон для сброса пароля
          </p>
        </div>
        <form className='mt-8 space-y-6' onSubmit={handleSubmit}>
          {error && (
            <div className='bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded'>
              {error}
            </div>
          )}
          <div>
            <label htmlFor='email_or_phone' className='sr-only'>
              Email или телефон
            </label>
            <input
              id='email_or_phone'
              name='email_or_phone'
              type='text'
              required
              className='appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
              placeholder='Email или телефон'
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div>
            <button
              type='submit'
              disabled={isLoading}
              className='group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed'
            >
              {isLoading ? 'Отправка...' : 'Отправить ссылку'}
            </button>
          </div>

          <div className='text-center'>
            <Link
              to='/login'
              className='font-medium text-blue-600 hover:text-blue-500'
            >
              Вернуться к входу
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
