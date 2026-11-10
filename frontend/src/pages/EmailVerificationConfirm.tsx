import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { useAuth } from '../contexts/useAuth'
import { getApiErrorMessage } from '../utils/apiError'

export default function EmailVerificationConfirm() {
  const { uidb64, token } = useParams<{ uidb64: string; token: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { refreshUser } = useAuth()
  const hasStartedConfirmation = useRef(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!uidb64 || !token || hasStartedConfirmation.current) {
      return
    }
    hasStartedConfirmation.current = true
    authApi.verifyEmailConfirm(uidb64, token)
      .then(async () => {
        await refreshUser()
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ['my-orders'] }),
          queryClient.invalidateQueries({ queryKey: ['my-requests'] }),
        ])
        navigate('/account?verified=1', { replace: true })
      })
      .catch((requestError) => setError(getApiErrorMessage(requestError, 'Не удалось подтвердить email.')))
  }, [navigate, queryClient, refreshUser, token, uidb64])

  if (!uidb64 || !token) {
    return <StateCard title="Не удалось подтвердить email"><p>Недействительная ссылка подтверждения.</p><Link to="/account" className="mt-5 inline-block font-medium text-blue-700 underline">Вернуться в профиль</Link></StateCard>
  }
  if (error) return <StateCard title="Не удалось подтвердить email"><p>{error}</p><Link to="/account" className="mt-5 inline-block font-medium text-blue-700 underline">Вернуться в профиль</Link></StateCard>
  return <main className="min-h-screen" aria-live="polite" aria-label="Подтверждаем email" />
}

function StateCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12"><section className="w-full max-w-lg rounded-lg bg-white p-8 text-center shadow-md"><h1 className="text-3xl font-bold text-gray-900">{title}</h1><div className="mt-4 text-gray-700">{children}</div></section></div>
}
