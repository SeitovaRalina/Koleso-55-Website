import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { excursionsApi } from '../api/excursions'
import { bookingsApi } from '../api/bookings'
import { useAuth } from '../contexts/useAuth'
import { formatApiFieldErrors } from '../utils/apiError'

export default function Booking() {
  const { excursionId, slotId } = useParams<{
    excursionId: string
    slotId: string
  }>()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuth()
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    patronymic: user?.patronymic || '',
    phone: user?.phone || '',
    email: user?.email || '',
    participants_count: 1,
    contact_method: 'call' as 'call' | 'whatsapp' | 'telegram' | 'email',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { data: excursion, isLoading: isLoadingExcursion } = useQuery({
    queryKey: ['excursion', excursionId],
    queryFn: () => excursionsApi.getExcursionById(Number(excursionId!)),
    enabled: !!excursionId,
  })

  const selectedSlot = excursion?.slots?.find(s => s.id === Number(slotId))

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', {
        state: { from: `/booking/${excursionId}/${slotId}` },
      })
    }
  }, [isAuthenticated, navigate, excursionId, slotId])

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        patronymic: user.patronymic || '',
        phone: user.phone || '',
        email: user.email || '',
      }))
    }
  }, [user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!selectedSlot) {
      setError('Слот не найден')
      return
    }

    if (formData.participants_count > selectedSlot.available_seats) {
      setError('Недостаточно доступных мест')
      return
    }

    setIsLoading(true)

    try {
      await bookingsApi.createOrder({
        excursion: Number(excursionId),
        slot: Number(slotId),
        num_participants: formData.participants_count,
        first_name: formData.first_name,
        last_name: formData.last_name,
        middle_name: formData.patronymic,
        phone: formData.phone,
        email: formData.email,
        contact_method: formData.contact_method,
      })
      navigate('/')
    } catch (err: unknown) {
      setError(formatApiFieldErrors(err, 'Ошибка создания заказа'))
      console.error('Booking error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoadingExcursion) {
    return (
      <div className='flex items-center justify-center min-h-screen'>
        <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600'></div>
      </div>
    )
  }

  if (!excursion || !selectedSlot) {
    return (
      <div className='flex items-center justify-center min-h-screen'>
        <div className='text-center'>
          <h2 className='text-2xl font-bold text-gray-900'>Ошибка</h2>
          <button
            onClick={() => navigate('/catalog')}
            className='text-blue-600 hover:underline mt-4'
          >
            Вернуться в каталог
          </button>
        </div>
      </div>
    )
  }

  const totalPrice = Number(excursion.price) * formData.participants_count

  return (
    <div className='min-h-screen bg-gray-50 py-8'>
      <div className='max-w-4xl mx-auto px-4 sm:px-6 lg:px-8'>
        <h1 className='text-3xl font-bold text-gray-900 mb-8'>
          Оформление бронирования
        </h1>

        <div className='grid grid-cols-1 lg:grid-cols-3 gap-8'>
          <div className='lg:col-span-2'>
            <form
              onSubmit={handleSubmit}
              className='bg-white rounded-lg shadow-md p-6 space-y-6'
            >
              {error && (
                <div className='bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded'>
                  {error}
                </div>
              )}

              <div>
                <h2 className='text-xl font-semibold mb-4'>
                  Информация об экскурсии
                </h2>
                <div className='bg-gray-50 p-4 rounded-lg'>
                  <h3 className='font-medium'>{excursion.title}</h3>
                  <p className='text-gray-600'>
                    {new Date(selectedSlot.date).toLocaleDateString('ru-RU')} в{' '}
                    {selectedSlot.time}
                  </p>
                  <p className='text-gray-600'>
                    Длительность: {Math.floor(excursion.duration / 60)}ч{' '}
                    {excursion.duration % 60}мин
                  </p>
                </div>
              </div>

              <div>
                <h2 className='text-xl font-semibold mb-4'>
                  Количество участников
                </h2>
                <div className='flex items-center gap-4'>
                  <button
                    type='button'
                    onClick={() =>
                      setFormData(prev => ({
                        ...prev,
                        participants_count: Math.max(
                          1,
                          prev.participants_count - 1,
                        ),
                      }))
                    }
                    className='w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100'
                  >
                    -
                  </button>
                  <span className='text-2xl font-medium'>
                    {formData.participants_count}
                  </span>
                  <button
                    type='button'
                    onClick={() =>
                      setFormData(prev => ({
                        ...prev,
                        participants_count: Math.min(
                          selectedSlot.available_seats,
                          prev.participants_count + 1,
                        ),
                      }))
                    }
                    className='w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100'
                  >
                    +
                  </button>
                </div>
                <p className='text-sm text-gray-500 mt-2'>
                  Доступно мест: {selectedSlot.available_seats}
                </p>
              </div>

              <div>
                <h2 className='text-xl font-semibold mb-4'>
                  Контактная информация
                </h2>
                <div className='space-y-4'>
                  <div>
                    <label className='block text-sm font-medium text-gray-700 mb-1'>
                      Имя *
                    </label>
                    <input
                      type='text'
                      required
                      className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                      value={formData.first_name}
                      onChange={e =>
                        setFormData({ ...formData, first_name: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className='block text-sm font-medium text-gray-700 mb-1'>
                      Фамилия *
                    </label>
                    <input
                      type='text'
                      required
                      className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                      value={formData.last_name}
                      onChange={e =>
                        setFormData({ ...formData, last_name: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className='block text-sm font-medium text-gray-700 mb-1'>
                      Отчество
                    </label>
                    <input
                      type='text'
                      className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                      value={formData.patronymic}
                      onChange={e =>
                        setFormData({ ...formData, patronymic: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className='block text-sm font-medium text-gray-700 mb-1'>
                      Телефон *
                    </label>
                    <input
                      type='tel'
                      required
                      className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                      value={formData.phone}
                      onChange={e =>
                        setFormData({ ...formData, phone: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className='block text-sm font-medium text-gray-700 mb-1'>
                      Email *
                    </label>
                    <input
                      type='email'
                      required
                      className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                      value={formData.email}
                      onChange={e =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className='block text-sm font-medium text-gray-700 mb-1'>
                      Способ связи *
                    </label>
                    <select
                      required
                      className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                      value={formData.contact_method}
                      onChange={e =>
                        setFormData({
                          ...formData,
                          contact_method: e.target.value as
                            | 'call'
                            | 'whatsapp'
                            | 'telegram'
                            | 'email',
                        })
                      }
                    >
                      <option value='call'>Звонок</option>
                      <option value='whatsapp'>WhatsApp</option>
                      <option value='telegram'>Telegram</option>
                      <option value='email'>Email</option>
                    </select>
                  </div>
                </div>
              </div>

              <button
                type='submit'
                disabled={isLoading}
                className='w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
              >
                {isLoading ? 'Создание заказа...' : 'Подтвердить бронирование'}
              </button>
            </form>
          </div>

          <div className='lg:col-span-1'>
            <div className='bg-white rounded-lg shadow-md p-6 sticky top-8'>
              <h2 className='text-xl font-semibold mb-4'>Итого</h2>
              <div className='space-y-2'>
                <div className='flex justify-between'>
                  <span className='text-gray-600'>Цена за человека:</span>
                  <span>{excursion.price} ₽</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-gray-600'>Количество:</span>
                  <span>{formData.participants_count}</span>
                </div>
                <div className='border-t pt-2 flex justify-between font-semibold'>
                  <span>Итого:</span>
                  <span className='text-blue-600'>{totalPrice} ₽</span>
                </div>
              </div>

              <div className='mt-6 p-4 bg-yellow-50 rounded-lg'>
                <p className='text-sm text-yellow-800'>
                  Оплата будет доступна после подтверждения заказа
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
