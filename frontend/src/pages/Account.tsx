import { useEffect, useState, useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../contexts/useAuth'
import { authApi } from '../api/auth'
import { bookingsApi } from '../api/bookings'
import { wishlistApi } from '../api/wishlist'
import { recommendationsApi } from '../api/recommendations'
import { ExcursionCard } from '../components/ui/ExcursionCard'
import { useHydratedExcursions } from '../hooks/useHydratedExcursions'
import type { Booking, UnifiedRequest } from '../types'
import { getApiErrorMessage } from '../utils/apiError'

const accountTabs = ['profile', 'bookings', 'requests', 'favorites', 'recommendations'] as const
type AccountTab = typeof accountTabs[number]

function getAccountTab(value: string | null): AccountTab {
  return accountTabs.includes(value as AccountTab) ? (value as AccountTab) : 'profile'
}

export default function Account() {
  const { user, updateUser, logout } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState<AccountTab>(() => getAccountTab(searchParams.get('tab')))
  const [requestPage, setRequestPage] = useState(1)
  const [profileForm, setProfileForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    patronymic: user?.patronymic || '',
    phone: user?.phone || '',
  })
  const [profileError, setProfileError] = useState('')
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [verificationMessage, setVerificationMessage] = useState('')
  const [verificationError, setVerificationError] = useState('')
  const [isSendingVerification, setIsSendingVerification] = useState(false)
  const [resendCooldown, setResendCooldown] = useState(0)

  useEffect(() => {
    setActiveTab(getAccountTab(searchParams.get('tab')))
  }, [searchParams])

  useEffect(() => {
    if (!resendCooldown) return
    const timer = window.setTimeout(() => setResendCooldown((value) => value - 1), 1000)
    return () => window.clearTimeout(timer)
  }, [resendCooldown])

  const { data: bookings, isLoading: isLoadingBookings } = useQuery({
    queryKey: ['my-orders'],
    queryFn: () => bookingsApi.getMyOrders(),
  })

  const { data: requests, isLoading: isLoadingRequests, error: requestsError } = useQuery({
    queryKey: ['my-requests', user?.id, requestPage],
    queryFn: () => authApi.getMyRequests(requestPage),
    enabled: !!user?.id && activeTab === 'requests',
  })

  const { data: wishlist, isLoading: isLoadingWishlist } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => wishlistApi.getWishlist(),
  })

  const { data: recommendations, isLoading: isLoadingRecommendations } = useQuery({
    queryKey: ['recommendations', user?.id],
    queryFn: () => recommendationsApi.getUserRecommendations(user!.id),
    enabled: !!user?.id,
  })

  const recommendationIds = useMemo(
    () => recommendations?.map((item) => item.excursion_id) ?? [],
    [recommendations],
  )

  const { data: recommendedExcursions = [], isLoading: isLoadingRecommended } = useHydratedExcursions(
    recommendationIds,
  )

  const cancelOrderMutation = useMutation({
    mutationFn: (orderId: number) => bookingsApi.cancelOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-orders'] })
    },
  })

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileError('')
    setIsSavingProfile(true)

    try {
      const updatedUser = await authApi.updateProfile(profileForm)
      updateUser(updatedUser)
    } catch (err: unknown) {
      setProfileError(getApiErrorMessage(err, 'Ошибка обновления профиля'))
    } finally {
      setIsSavingProfile(false)
    }
  }

  const handleCancelOrder = async (orderId: number) => {
    if (window.confirm('Вы уверены, что хотите отменить заказ?')) {
      try {
        await cancelOrderMutation.mutateAsync(orderId)
      } catch (error) {
        console.error('Failed to cancel order:', error)
      }
    }
  }

  const handleResendVerification = async () => {
    setVerificationError('')
    setVerificationMessage('')
    setIsSendingVerification(true)
    try {
      await authApi.verifyEmail()
      setVerificationMessage('Письмо отправлено. Проверьте входящие и папку «Спам».')
      setResendCooldown(60)
    } catch (error) {
      setVerificationError(getApiErrorMessage(error, 'Не удалось отправить письмо. Попробуйте позже.'))
    } finally {
      setIsSendingVerification(false)
    }
  }

  const getStatusBadge = (status: string, label?: string) => {
    const colors: Record<string, string> = {
      new: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-amber-100 text-amber-800',
      confirmed: 'bg-green-100 text-green-800',
      paid: 'bg-purple-100 text-purple-800',
      cancelled: 'bg-red-100 text-red-800',
      completed: 'bg-green-100 text-green-800',
      closed: 'bg-green-100 text-green-800',
    }
    const labels: Record<string, string> = {
      new: 'Новый',
      in_progress: 'В работе',
      confirmed: 'Подтверждён',
      paid: 'Оплачен',
      cancelled: 'Отменён',
      completed: 'Выполнен',
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100'}`}>
        {label || labels[status] || status}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Личный кабинет</h1>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="border-b">
            <nav className="flex -mb-px overflow-x-auto" aria-label="Разделы личного кабинета">
              {accountTabs.map((tab) => (
                <button
                  key={tab}
                  onClick={() => {
                    setActiveTab(tab)
                    setSearchParams(tab === 'profile' ? {} : { tab })
                  }}
                  className={`px-6 py-4 text-sm font-medium ${
                    activeTab === tab
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab === 'profile' && 'Профиль'}
                  {tab === 'bookings' && 'Мои бронирования'}
                  {tab === 'requests' && 'Мои заявки'}
                  {tab === 'favorites' && 'Избранное'}
                  {tab === 'recommendations' && 'Рекомендации'}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {searchParams.get('verified') === '1' && (
              <p role="status" className="mb-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">Email подтверждён. Заявки и бронирования с этим адресом добавлены в кабинет.</p>
            )}
            {activeTab === 'requests' && (
              <section aria-label="Мои заявки" className="space-y-4">
                {!user?.is_email_verified && <VerificationHistoryHint />}
                {isLoadingRequests && <p role="status">Загружаем заявки...</p>}
                {requestsError && <p role="alert" className="text-red-700">Не удалось загрузить заявки. Обновите страницу и попробуйте снова.</p>}
                {!isLoadingRequests && !requestsError && requests?.results.length === 0 && <p className="py-8 text-center text-gray-500">У вас пока нет заявок.</p>}
                {requests?.results.map((request: UnifiedRequest) => (
                  <article key={`${request.type}-${request.id}`} className="rounded-lg border p-4 space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      {request.excursion ? <Link to={`/excursion/${request.excursion}`} className="font-medium text-blue-700 hover:underline">{request.title}</Link> : <h2 className="font-medium">{request.title}</h2>}
                      {getStatusBadge(request.status, request.status_display)}
                    </div>
                    <p className="whitespace-pre-wrap break-words text-sm text-gray-600">{request.summary}</p>
                    <time dateTime={request.created_at} className="block text-xs text-gray-500">Отправлено: {new Date(request.created_at).toLocaleString('ru-RU')}</time>
                  </article>
                ))}
                {(requests?.previous || requests?.next) && (
                  <div className="flex gap-3">
                    <button type="button" disabled={!requests.previous} onClick={() => setRequestPage((page) => page - 1)} className="rounded border px-3 py-2 disabled:opacity-50">Назад</button>
                    <button type="button" disabled={!requests.next} onClick={() => setRequestPage((page) => page + 1)} className="rounded border px-3 py-2 disabled:opacity-50">Далее</button>
                  </div>
                )}
              </section>
            )}
            {activeTab === 'profile' && (
              <form onSubmit={handleSaveProfile} className="max-w-2xl space-y-6">
                {profileError && (
                  <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                    {profileError}
                  </div>
                )}
                {!user?.is_email_verified && (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950" role="status">
                    <p className="font-medium">Подтвердите email, чтобы увидеть прошлые бронирования и заявки.</p>
                    <p className="mt-1">Письмо придёт на {user?.email}. После подтверждения заявки и бронирования с этим адресом появятся в кабинете.</p>
                    <button type="button" onClick={handleResendVerification} disabled={isSendingVerification || resendCooldown > 0} className="mt-3 rounded border border-amber-700 px-3 py-2 font-medium disabled:cursor-not-allowed disabled:opacity-60">{isSendingVerification ? 'Отправляем…' : resendCooldown > 0 ? `Повторить через ${resendCooldown} с` : 'Отправить письмо ещё раз'}</button>
                    {verificationMessage && <p className="mt-2 text-green-800">{verificationMessage}</p>}
                    {verificationError && <p className="mt-2 text-red-700">{verificationError}</p>}
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Email нельзя изменить</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Имя *</label>
                  <input
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={profileForm.first_name}
                    onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Фамилия *</label>
                  <input
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={profileForm.last_name}
                    onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Отчество</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={profileForm.patronymic}
                    onChange={(e) => setProfileForm({ ...profileForm, patronymic: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Телефон *</label>
                  <input
                    type="tel"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={profileForm.phone}
                    onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    type="submit"
                    disabled={isSavingProfile}
                    className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isSavingProfile ? 'Сохранение...' : 'Сохранить'}
                  </button>
                  <button
                    type="button"
                    onClick={logout}
                    className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700"
                  >
                    Выйти
                  </button>
                </div>
              </form>
            )}

            {activeTab === 'bookings' && (
              <div>
                {isLoadingBookings ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                ) : bookings?.results.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    У вас пока нет бронирований
                    {!user?.is_email_verified && <VerificationHistoryHint />}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {bookings?.results.map((booking: Booking) => (
                      <div key={booking.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          {booking.excursion_id ? (
                            <Link
                              to={`/excursion/${booking.excursion_id}`}
                              className="font-medium text-gray-900 hover:text-blue-600 hover:underline"
                            >
                              {booking.excursion_title}
                            </Link>
                          ) : (
                            <h3 className="font-medium">{booking.excursion_title}</h3>
                          )}
                          {getStatusBadge(booking.status)}
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>Дата: {new Date(booking.slot_date || booking.slot_datetime).toLocaleDateString('ru-RU')}</p>
                          <p>Время: {booking.slot_time}</p>
                          <p>Участников: {booking.participants_count || booking.num_participants}</p>
                          {booking.total_price && <p>Сумма: {booking.total_price} ₽</p>}
                        </div>
                        {(booking.status === 'new' || booking.status === 'confirmed') && (
                          <button
                            onClick={() => handleCancelOrder(booking.id)}
                            className="mt-3 text-sm text-red-600 hover:text-red-700"
                          >
                            Отменить заказ
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'favorites' && (
              <div>
                {isLoadingWishlist ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                ) : wishlist?.results.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    У вас пока нет избранных экскурсий
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    {wishlist?.results.map((item) => (
                      <ExcursionCard key={item.id} excursion={item.excursion} source="wishlist" />
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div>
                {isLoadingRecommendations || isLoadingRecommended ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                ) : recommendedExcursions.length > 0 ? (
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    {recommendedExcursions.map((excursion) => (
                      <ExcursionCard
                        key={excursion.id}
                        excursion={excursion}
                        source="recommendation"
                      />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Рекомендации появятся после просмотра экскурсий
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function VerificationHistoryHint() {
  return (
    <p className="mt-2 text-sm text-amber-800">Если бронирование или заявка были созданы до регистрации, подтвердите email в <Link to="/account" className="font-medium underline">профиле</Link> — тогда записи с тем же email появятся здесь.</p>
  )
}
