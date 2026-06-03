import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import { authApi } from '../api/auth'
import { bookingsApi } from '../api/bookings'
import { wishlistApi } from '../api/wishlist'
import { recommendationsApi } from '../api/recommendations'
import type { Excursion, Booking } from '../types'

export default function Account() {
  const { user, updateUser, logout } = useAuth()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('profile')
  const [profileForm, setProfileForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    patronymic: user?.patronymic || '',
    phone: user?.phone || '',
  })
  const [profileError, setProfileError] = useState('')
  const [isSavingProfile, setIsSavingProfile] = useState(false)

  const { data: bookings, isLoading: isLoadingBookings } = useQuery({
    queryKey: ['my-orders'],
    queryFn: () => bookingsApi.getMyOrders(),
  })

  const { data: wishlist, isLoading: isLoadingWishlist } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => wishlistApi.getWishlist(),
  })

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', user?.id],
    queryFn: () => recommendationsApi.getUserRecommendations(user!.id),
    enabled: !!user?.id,
  })

  const cancelOrderMutation = useMutation({
    mutationFn: (orderId: number) => bookingsApi.cancelOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-orders'] })
    },
  })

  const removeFromWishlistMutation = useMutation({
    mutationFn: (excursionId: number) => wishlistApi.removeFromWishlist(excursionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] })
    },
  })

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileError('')
    setIsSavingProfile(true)

    try {
      const updatedUser = await authApi.updateProfile(profileForm)
      updateUser(updatedUser)
    } catch (err: any) {
      setProfileError(err.response?.data?.detail || 'Ошибка обновления профиля')
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

  const handleRemoveFromWishlist = async (excursionId: number) => {
    try {
      await removeFromWishlistMutation.mutateAsync(excursionId)
    } catch (error) {
      console.error('Failed to remove from wishlist:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-blue-100 text-blue-800',
      confirmed: 'bg-green-100 text-green-800',
      paid: 'bg-purple-100 text-purple-800',
      cancelled: 'bg-red-100 text-red-800',
      completed: 'bg-gray-100 text-gray-800',
    }
    const labels: Record<string, string> = {
      new: 'Новый',
      confirmed: 'Подтверждён',
      paid: 'Оплачен',
      cancelled: 'Отменён',
      completed: 'Выполнен',
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100'}`}>
        {labels[status] || status}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Личный кабинет</h1>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="border-b">
            <nav className="flex -mb-px">
              {['profile', 'bookings', 'favorites', 'recommendations'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-4 text-sm font-medium ${
                    activeTab === tab
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab === 'profile' && 'Профиль'}
                  {tab === 'bookings' && 'Мои бронирования'}
                  {tab === 'favorites' && 'Избранное'}
                  {tab === 'recommendations' && 'Рекомендации'}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'profile' && (
              <form onSubmit={handleSaveProfile} className="max-w-2xl space-y-6">
                {profileError && (
                  <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                    {profileError}
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
                  </div>
                ) : (
                  <div className="space-y-4">
                    {bookings?.results.map((booking: Booking) => (
                      <div key={booking.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-medium">{booking.excursion_title}</h3>
                          {getStatusBadge(booking.status)}
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>Дата: {new Date(booking.slot_date).toLocaleDateString('ru-RU')}</p>
                          <p>Время: {booking.slot_time}</p>
                          <p>Участников: {booking.participants_count}</p>
                          <p>Сумма: {booking.total_price} ₽</p>
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
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {wishlist?.results.map((excursion: Excursion) => (
                      <div key={excursion.id} className="border rounded-lg overflow-hidden">
                        {excursion.main_image && (
                          <img
                            src={excursion.main_image}
                            alt={excursion.title}
                            className="w-full h-48 object-cover"
                          />
                        )}
                        <div className="p-4">
                          <h3 className="font-medium mb-2">{excursion.title}</h3>
                          <p className="text-blue-600 font-medium">{excursion.price} ₽</p>
                          <button
                            onClick={() => handleRemoveFromWishlist(excursion.id)}
                            className="mt-2 text-sm text-red-600 hover:text-red-700"
                          >
                            Удалить из избранного
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div>
                {recommendations && recommendations.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {recommendations.map((rec) => (
                      <div key={rec.excursion_id} className="border rounded-lg overflow-hidden">
                        {rec.excursion?.main_image && (
                          <img
                            src={rec.excursion.main_image}
                            alt={rec.excursion.title}
                            className="w-full h-48 object-cover"
                          />
                        )}
                        <div className="p-4">
                          <h3 className="font-medium mb-2">{rec.excursion?.title}</h3>
                          <p className="text-sm text-gray-600 mb-2">
                            {rec.excursion?.short_description}
                          </p>
                          <p className="text-blue-600 font-medium">{rec.excursion?.price} ₽</p>
                        </div>
                      </div>
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
