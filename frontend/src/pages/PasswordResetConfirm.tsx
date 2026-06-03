import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { authApi } from '../api/auth'

export default function PasswordResetConfirm() {
  const { uidb64, token } = useParams<{ uidb64: string; token: string }>()
  const [formData, setFormData] = useState({
    new_password: '',
    confirm_password: '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.new_password !== formData.confirm_password) {
      setError('Пароли не совпадают')
      return
    }

    if (!uidb64 || !token) {
      setError('Неверная ссылка сброса пароля')
      return
    }

    setIsLoading(true)

    try {
      await authApi.passwordResetConfirm({
        uidb64,
        token,
        new_password: formData.new_password,
      })
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сброса пароля')
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
              Пароль изменен
            </h2>
            <p className='mt-2 text-sm text-gray-600'>
              Теперь вы можете войти с новым паролем
            </p>
          </div>
          <div className='text-center'>
            <Link
              to='/login'
              className='font-medium text-blue-600 hover:text-blue-500'
            >
              Перейти к входу
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
            Установите новый пароль
          </h2>
        </div>
        <form className='mt-8 space-y-6' onSubmit={handleSubmit}>
          {error && (
            <div className='bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded'>
              {error}
            </div>
          )}
          <div className='space-y-4'>
            <div>
              <label htmlFor='new_password' className='sr-only'>
                Новый пароль
              </label>
              <input
                id='new_password'
                name='new_password'
                type='password'
                required
                minLength={8}
                className='appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
                placeholder='Новый пароль (минимум 8 символов)'
                value={formData.new_password}
                onChange={e =>
                  setFormData({ ...formData, new_password: e.target.value })
                }
              />
            </div>
            <div>
              <label htmlFor='confirm_password' className='sr-only'>
                Подтвердите пароль
              </label>
              <input
                id='confirm_password'
                name='confirm_password'
                type='password'
                required
                minLength={8}
                className='appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
                placeholder='Подтвердите пароль'
                value={formData.confirm_password}
                onChange={e =>
                  setFormData({ ...formData, confirm_password: e.target.value })
                }
              />
            </div>
          </div>

          <div>
            <button
              type='submit'
              disabled={isLoading}
              className='group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed'
            >
              {isLoading ? 'Сохранение...' : 'Установить пароль'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
