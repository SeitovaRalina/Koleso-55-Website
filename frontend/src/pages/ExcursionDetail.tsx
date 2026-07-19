import { useState, useEffect, useRef, useMemo } from 'react'
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { excursionsApi } from '../api/excursions'
import { analyticsApi } from '../api/analytics'
import { wishlistApi } from '../api/wishlist'
import { recommendationsApi } from '../api/recommendations'
import { bookingsApi } from '../api/bookings'
import { authApi } from '../api/auth'
import { useAuth } from '../contexts/useAuth'
import { useHydratedExcursions } from '../hooks/useHydratedExcursions'
import type {
  ExcursionSlot,
  Review,
  Excursion,
  ReviewImage,
  TicketType,
} from '../types'
import { FavoriteIcon } from '../components/ui/FavoriteIcon'
import { ExcursionCard } from '../components/ui/ExcursionCard'
import { ExcursionPhotoGallery } from '../components/excursion/ExcursionPhotoGallery'
import { getApiErrorMessage } from '../utils/apiError'

type ContactMethod = 'call' | 'whatsapp' | 'telegram' | 'max' | 'email'

interface BookingFormState {
  fullName: string
  phone: string
  email: string
  contactMethod: ContactMethod
  participantNames: string
  comment: string
  personalDataConsent: boolean
  offerConsent: boolean
  updateProfile: boolean
}

const contactMethods: Array<{ value: ContactMethod; label: string }> = [
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'telegram', label: 'Telegram' },
  { value: 'max', label: 'MAX' },
  { value: 'call', label: 'Звонок' },
  { value: 'email', label: 'Email' },
]

function getUserFullName(user: { first_name?: string; last_name?: string; patronymic?: string } | null) {
  return [user?.last_name, user?.first_name, user?.patronymic].filter(Boolean).join(' ').trim()
}

function splitFullName(fullName: string) {
  const [lastName = '', firstName = '', ...middleNameParts] = fullName.trim().split(/\s+/).filter(Boolean)
  return {
    firstName: firstName || lastName,
    lastName: firstName ? lastName : '',
    middleName: middleNameParts.join(' '),
  }
}

export default function ExcursionDetail() {
  const { excursionId } = useParams<{ excursionId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { user, isAuthenticated, updateUser } = useAuth()
  const [selectedSlot, setSelectedSlot] = useState<ExcursionSlot | null>(null)
  const [isFavorite, setIsFavorite] = useState(false)
  const viewIdRef = useRef<number | null>(null)
  const [showAllReviews, setShowAllReviews] = useState(false)
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false)
  const [participantCount, setParticipantCount] = useState(1)
  const [bookingForm, setBookingForm] = useState<BookingFormState>({
    fullName: '',
    phone: '',
    email: '',
    contactMethod: 'whatsapp',
    participantNames: '',
    comment: '',
    personalDataConsent: false,
    offerConsent: false,
    updateProfile: false,
  })
  const [bookingError, setBookingError] = useState('')
  const [bookingSuccess, setBookingSuccess] = useState('')
  const [isBookingSubmitting, setIsBookingSubmitting] = useState(false)
  const [questionContactMethod, setQuestionContactMethod] = useState<ContactMethod>('whatsapp')
  const { data: excursion, isLoading, error } = useQuery<Excursion>({
    queryKey: ['excursion', excursionId],
    queryFn: () => excursionsApi.getExcursionById(Number(excursionId!)),
    enabled: !!excursionId,
  })

  const { data: similarRecommendations } = useQuery({
    queryKey: ['similar', excursion?.id],
    queryFn: () => recommendationsApi.getSimilarExcursions(excursion!.id),
    enabled: !!excursion?.id,
  })

  const similarIds = useMemo(
    () => similarRecommendations?.map((item) => item.excursion_id) ?? [],
    [similarRecommendations],
  )

  const { data: similarExcursions = [] } = useHydratedExcursions(similarIds)

  useEffect(() => {
    if (!isAuthenticated || !user) {
      setBookingForm((current) => ({
        ...current,
        updateProfile: false,
      }))
      return
    }

    setBookingForm((current) => ({
      ...current,
      fullName: current.fullName || getUserFullName(user),
      phone: current.phone || user.phone || '',
      email: user.email || current.email,
      updateProfile: true,
    }))
  }, [isAuthenticated, user])

  useEffect(() => {
    const stateSource = location.state?.source as 'search' | 'catalog' | 'recommendation' | 'similar' | 'direct' | undefined
    const fromPath = location.state?.from as string | undefined

    if (excursion) {
      // Generate or get session_id for all users
      let sessionId = localStorage.getItem('session_id')
      if (!sessionId) {
        sessionId = crypto.randomUUID()
        localStorage.setItem('session_id', sessionId)
      }

      // Determine source based on location.state or previous path (only on initial load)
      let source: 'search' | 'catalog' | 'recommendation' | 'similar' | 'direct' = 'direct'
      
      if (stateSource) {
        source = stateSource
      } else if (fromPath) {
        if (fromPath.includes('/catalog')) {
          source = 'catalog'
        } else if (fromPath.includes('/search')) {
          source = 'search'
        } else if (fromPath.includes('/recommendations')) {
          source = 'recommendation'
        } else if (fromPath.includes('/excursion')) {
          source = 'similar'
        }
      }

      analyticsApi.startView({
        excursion_id: excursion.id,
        session_id: sessionId,
        source,
      }).then((response) => {
        console.log('View started:', response)
        viewIdRef.current = response.view_id
      }).catch(error => {
        console.error('Failed to start view tracking:', error)
      })

      if (isAuthenticated) {
        wishlistApi.checkInWishlist(excursion.id).then((response) => {
          setIsFavorite(response.is_in_wishlist)
        })
      }
    }

    return () => {
      if (viewIdRef.current) {
        analyticsApi.endView({ view_id: viewIdRef.current })
      }
    }
  }, [excursion, isAuthenticated, location.state?.from, location.state?.source])

  useEffect(() => {
    const heartbeat = setInterval(() => {
      if (viewIdRef.current) {
        console.log('Sending heartbeat for view:', viewIdRef.current)
        analyticsApi.heartbeatView({ view_id: viewIdRef.current, elapsed_seconds: 5 })
          .then(() => console.log('Heartbeat sent successfully'))
          .catch(err => console.error('Heartbeat failed:', err))
      }
    }, 5000)

    return () => clearInterval(heartbeat)
  }, [])

  const handleToggleFavorite = async () => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    try {
      if (isFavorite) {
        await wishlistApi.removeFromWishlist(excursion!.id)
        setIsFavorite(false)
      } else {
        await wishlistApi.addToWishlist(excursion!.id)
        setIsFavorite(true)
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }

  const handleBookNow = () => {
    if (!selectedSlot) {
      alert('Пожалуйста, выберите дату и время')
      return
    }
    setBookingError('')
    setBookingSuccess('')
    setIsBookingModalOpen(true)
  }

  const handleBookingSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!excursion || !selectedSlot) {
      setBookingError('Выберите дату и время экскурсии')
      return
    }

    if (participantCount > selectedSlot.available_seats) {
      setBookingError('В выбранном слоте недостаточно мест')
      return
    }

    if (bookingForm.contactMethod === 'email' && !bookingForm.email.trim()) {
      setBookingError('Для связи по Email укажите email')
      return
    }

    if (!bookingForm.personalDataConsent || !bookingForm.offerConsent) {
      setBookingError('Подтвердите согласия перед отправкой заявки')
      return
    }

    const { firstName, lastName, middleName } = splitFullName(bookingForm.fullName)
    if (!firstName) {
      setBookingError('Укажите ФИО')
      return
    }

    setBookingError('')
    setBookingSuccess('')
    setIsBookingSubmitting(true)

    try {
      await bookingsApi.createOrder({
        excursion: excursion.id,
        slot: selectedSlot.id,
        first_name: firstName,
        last_name: lastName,
        middle_name: middleName,
        phone: bookingForm.phone.trim(),
        email: bookingForm.email.trim(),
        num_participants: participantCount,
        contact_method: bookingForm.contactMethod,
        comment: [
          bookingForm.participantNames.trim() && `ФИО других участников: ${bookingForm.participantNames.trim()}`,
          bookingForm.comment.trim(),
        ].filter(Boolean).join('\n\n'),
        save_to_profile: isAuthenticated ? bookingForm.updateProfile : false,
      })

      if (isAuthenticated && user && bookingForm.updateProfile) {
        try {
          const updatedUser = await authApi.updateProfile({
            first_name: firstName,
            last_name: lastName,
            patronymic: middleName,
            phone: bookingForm.phone.trim(),
          })
          updateUser(updatedUser)
        } catch (profileError) {
          console.error('Failed to update profile after booking:', profileError)
        }
      }

      setBookingSuccess('Заказ успешно создан. Статус заказа можно отслеживать в личном кабинете.')
      setBookingForm((current) => ({
        ...current,
        participantNames: '',
        comment: '',
        personalDataConsent: false,
        offerConsent: false,
      }))
    } catch (err: unknown) {
      setBookingError(getApiErrorMessage(err, 'Не удалось создать заказ. Проверьте данные и попробуйте ещё раз.'))
    } finally {
      setIsBookingSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !excursion) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Экскурсия не найдена</h2>
          <Link to="/catalog" className="text-blue-600 hover:underline mt-4 inline-block">
            Вернуться в каталог
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero-блок с галереей */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
          <div className="relative p-4 sm:p-6">
            <ExcursionPhotoGallery
              images={excursion.images}
              reviews={excursion.approved_reviews}
              title={excursion.title}
            />
          </div>

          {/* Название и характеристики */}
          <div className="p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                {excursion.category.name}
              </span>
              <span className="px-3 py-1 bg-gray-100 text-gray-800 text-sm rounded-full">
                {excursion.location_type_display}
              </span>
            </div>

            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <h1 className="text-3xl font-bold text-gray-900">{excursion.title}</h1>
              <button
                type="button"
                onClick={handleToggleFavorite}
                aria-label={isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'}
                className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-700 transition hover:bg-brand-mist hover:text-brand-deep focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-sky"
              >
                <FavoriteIcon active={isFavorite} variant="solid" className="h-6 w-6" />
              </button>
            </div>

            {/* Основные характеристики */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <div className="text-sm text-gray-500">Длительность</div>
                  <div className="font-medium">{Math.floor(excursion.duration / 60)}ч {excursion.duration % 60}мин</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                <div>
                  <div className="text-sm text-gray-500">Формат</div>
                  <div className="font-medium">{excursion.tour_format_display}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <div>
                  <div className="text-sm text-gray-500">Группа</div>
                  <div className="font-medium">до {excursion.group_size} чел</div>
                </div>
              </div>
              <div className="flex items-center gap-2 cursor-pointer hover:text-blue-600 transition-colors">
                <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <div>
                  <div className="text-sm text-gray-500">Рейтинг</div>
                  <div className="font-medium">{excursion.average_rating || '-'} ({excursion.review_count})</div>
                </div>
              </div>
            </div>

            <p className="text-gray-600 mb-4">{excursion.short_description}</p>
          </div>
        </div>

        {/* Grid layout: контент + sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Левая колонка: контент */}
          <div className="lg:col-span-2 space-y-8">
            {/* Подробное описание */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold mb-4">Подробное описание</h2>
              <p className="text-gray-700 whitespace-pre-line">{excursion.description}</p>
            </div>

            {/* Программа поездки */}
            {excursion.program_days && excursion.program_days.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-4">Программа поездки</h2>
                <div className="space-y-4">
                  {excursion.program_days.map((day) => (
                    <div key={day.id} className="border rounded-lg">
                      <button className="w-full p-4 text-left flex justify-between items-center hover:bg-gray-50">
                        <span className="font-medium">День {day.day_number}: {day.title}</span>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      <div className="p-4 pt-0 text-gray-600">
                        {day.description}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Отзывы */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold mb-4">Отзывы путешественников</h2>
              <div className="flex items-center gap-6 mb-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-yellow-400">★ {excursion.average_rating || '-'}</div>
                  <div className="text-gray-600">{excursion.review_count} отзывов</div>
                </div>
                {excursion.rating_distribution && (
                  <div className="flex-1">
                    {[5, 4, 3, 2, 1].map((star) => (
                      <div key={star} className="flex items-center gap-2 mb-1">
                        <span className="text-sm w-6">{star}★</span>
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-yellow-400 h-2 rounded-full"
                            style={{
                              width: excursion.review_count > 0 && excursion.rating_distribution
                                ? `${((excursion.rating_distribution[star as keyof typeof excursion.rating_distribution] ?? 0) / excursion.review_count) * 100}%`
                                : '0%'
                            }}
                          />
                        </div>
                        <span className="text-sm text-gray-600 w-8">
                          {excursion.rating_distribution?.[star as keyof typeof excursion.rating_distribution] || 0}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-4">
                {(showAllReviews ? excursion.approved_reviews : excursion.approved_reviews?.slice(0, 5))?.map((review: Review) => (
                  <div key={review.id} className="border-b pb-4 last:border-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">{review.user_name}</div>
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <svg
                            key={i}
                            className={`w-4 h-4 ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}`}
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                    </div>
                    <p className="text-gray-700">{review.text}</p>
                    {review.images && review.images.length > 0 && (
                      <div className="mt-2 flex gap-2">
                        {review.images.map((photo: ReviewImage) => (
                          <img key={photo.id} src={photo.image} alt="" className="w-20 h-20 object-cover rounded" />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {excursion.approved_reviews && excursion.approved_reviews.length > 5 && (
                <button
                  onClick={() => setShowAllReviews(!showAllReviews)}
                  className="text-blue-600 hover:underline"
                >
                  {showAllReviews ? 'Свернуть отзывы' : 'Показать все отзывы'}
                </button>
              )}
            </div>

            {/* Практическая информация */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold mb-4">Практическая информация</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {excursion.included_in_price && (
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Что входит в стоимость
                    </h3>
                    <p className="text-gray-600 whitespace-pre-line text-sm">{excursion.included_in_price}</p>
                  </div>
                )}
                {excursion.not_included_in_price && (
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                      <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Что не входит в стоимость
                    </h3>
                    <p className="text-gray-600 whitespace-pre-line text-sm">{excursion.not_included_in_price}</p>
                  </div>
                )}
                {excursion.what_to_bring && (
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      Что взять с собой
                    </h3>
                    <p className="text-gray-600 whitespace-pre-line text-sm">{excursion.what_to_bring}</p>
                  </div>
                )}
                {excursion.meeting_point && (
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                      <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Место встречи
                    </h3>
                    <p className="text-gray-600 text-sm">{excursion.meeting_point}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Правая колонка: sidebar бронирования */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
              <h3 className="text-xl font-bold mb-4">Бронирование</h3>
              <div className="text-3xl font-bold text-blue-600 mb-6">
                от {excursion.price} ₽
              </div>

              {/* Типы билетов */}
              {excursion.ticket_types && excursion.ticket_types.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold mb-3">Тип билета</h4>
                  <div className="space-y-2">
                    {excursion.ticket_types.filter((t: TicketType) => t.is_active).map((ticket: TicketType) => (
                      <label key={ticket.id} className="flex items-center gap-2 p-2 border rounded cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="ticket_type" className="w-4 h-4" />
                        <span>{ticket.name}</span>
                        <span className="ml-auto font-medium">{ticket.price} ₽</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Слоты */}
              <div className="mb-6">
                <h4 className="font-semibold mb-3">Выберите дату и время</h4>
                <div className="space-y-2">
                  {excursion.slots?.map((slot: ExcursionSlot) => (
                    <button
                      key={slot.id}
                      onClick={() => setSelectedSlot(slot)}
                      disabled={!slot.is_available}
                      className={`w-full p-3 border rounded-lg text-left transition-colors ${
                        selectedSlot?.id === slot.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      } ${!slot.is_available ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <div className="font-medium">{new Date(slot.date).toLocaleDateString('ru-RU')}</div>
                      <div className="text-sm text-gray-600">{slot.time}</div>
                      <div className="text-xs text-gray-500">
                        Осталось мест: {slot.available_seats}/{slot.max_participants}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Количество участников */}
              <div className="mb-6">
                <h4 className="font-semibold mb-3">Количество участников</h4>
                <div className="flex items-center gap-3">
                  <button 
                    onClick={() => setParticipantCount(Math.max(1, participantCount - 1))}
                    className="w-10 h-10 border rounded-lg hover:bg-gray-50"
                  >-</button>
                  <span className="text-xl font-medium">{participantCount}</span>
                  <button 
                    onClick={() => setParticipantCount(Math.min(selectedSlot?.available_seats ?? excursion.group_size, participantCount + 1))}
                    disabled={participantCount >= (selectedSlot?.available_seats ?? excursion.group_size)}
                    className="w-10 h-10 border rounded-lg hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >+</button>
                </div>
              </div>

              <button
                onClick={handleBookNow}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Забронировать место
              </button>
            </div>
          </div>
        </div>

        {/* Блок поддержки - на всю ширину */}
        <div className="mt-8 rounded-lg bg-white p-6 shadow-md">
          <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Остались вопросы?</h2>
              <p className="mt-3 text-gray-600">
                Напишите нам, если нужно уточнить маршрут, место встречи, состав группы или условия бронирования.
                Менеджер ответит удобным для вас способом и поможет выбрать подходящий слот.
              </p>
            </div>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ваше имя</label>
                <input type="text" className="w-full border rounded-lg p-2" placeholder="Как к вам обращаться?" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
                <input type="tel" className="w-full border rounded-lg p-2" placeholder="+7 (___) ___-__-__" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Способ связи</label>
                <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
                  {contactMethods.map((method) => (
                    <label key={method.value} className="flex items-center gap-2 rounded border p-2 hover:bg-gray-50">
                      <input
                        type="radio"
                        name="question_contact_method"
                        value={method.value}
                        checked={questionContactMethod === method.value}
                        onChange={() => setQuestionContactMethod(method.value)}
                        className="h-4 w-4"
                      />
                      <span className="text-sm">{method.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Сообщение</label>
                <textarea className="w-full border rounded-lg p-2" rows={3} placeholder="Ваш вопрос..." />
              </div>
              <button type="submit" className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                Отправить вопрос
              </button>
            </form>
          </div>
        </div>

        {/* Похожие экскурсии - на всю ширину */}
        {similarExcursions.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mt-8">
            <h3 className="text-xl font-bold mb-4">Вам может понравиться</h3>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {similarExcursions.slice(0, 4).map((similarExcursion) => (
                <ExcursionCard
                  key={similarExcursion.id}
                  excursion={similarExcursion}
                  source="similar"
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Модальное окно бронирования */}
      {isBookingModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Бронирование</h2>
                <button
                  onClick={() => setIsBookingModalOpen(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Ваше бронирование */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold mb-3">Ваше бронирование</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Экскурсия:</span>
                    <span className="font-medium">{excursion.title}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Дата и время:</span>
                    <span className="font-medium">
                      {selectedSlot && new Date(selectedSlot.date).toLocaleDateString('ru-RU')} {selectedSlot?.time}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Участников:</span>
                    <span className="font-medium">{participantCount} чел</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Итого:</span>
                    <span className="font-bold text-blue-600">
                      от {excursion.price} ₽ за человека
                    </span>
                  </div>
                </div>
                <p className="mt-3 text-xs text-gray-500">
                  Слот окончательно занимается после подтверждения оплаты или менеджером.
                </p>
              </div>

              {bookingSuccess ? (
                <div className="rounded-lg border border-green-200 bg-green-50 p-5">
                  <h3 className="text-lg font-semibold text-green-800">Заказ успешно создан</h3>
                  <p className="mt-2 text-sm text-green-700">
                    Статус заказа можно отслеживать в личном кабинете.
                  </p>
                  <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                    {isAuthenticated ? (
                      <Link
                        to="/account?tab=bookings"
                        className="inline-flex justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                      >
                        Перейти в личный кабинет
                      </Link>
                    ) : (
                      <Link
                        to="/login"
                        className="inline-flex justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                      >
                        Войти и привязать заказ
                      </Link>
                    )}
                    <button
                      type="button"
                      onClick={() => setIsBookingModalOpen(false)}
                      className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Закрыть
                    </button>
                  </div>
                </div>
              ) : (
                <>
              {bookingError && (
                <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {bookingError}
                </div>
              )}

              {isAuthenticated ? (
                <div className="mb-4 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-gray-700">
                  Данные автоматически заполнены из вашего аккаунта. Email нельзя изменить вручную.
                </div>
              ) : (
                <div className="mb-4 rounded-lg border border-gray-200 px-4 py-3 text-sm text-gray-600">
                  Можно оформить без регистрации. Войдите или зарегистрируйтесь, чтобы данные подставлялись автоматически и заказ появился в истории поездок.
                  <div className="mt-2 flex gap-3">
                    <Link to="/login" className="font-semibold text-blue-600 hover:underline">Войти</Link>
                    <Link to="/register" className="font-semibold text-blue-600 hover:underline">Зарегистрироваться</Link>
                  </div>
                </div>
              )}

              {/* Контактные данные */}
              <form onSubmit={handleBookingSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ФИО *</label>
                  <input
                    type="text"
                    className="w-full border rounded-lg p-2"
                    placeholder="Иванов Иван Иванович"
                    required
                    value={bookingForm.fullName}
                    onChange={(e) => setBookingForm({ ...bookingForm, fullName: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Телефон *</label>
                  <input
                    type="tel"
                    className="w-full border rounded-lg p-2"
                    placeholder="+7 (___) ___-__-__"
                    required
                    value={bookingForm.phone}
                    onChange={(e) => setBookingForm({ ...bookingForm, phone: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    className="w-full border rounded-lg p-2 disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="email@example.com"
                    required={bookingForm.contactMethod === 'email'}
                    disabled={isAuthenticated}
                    value={bookingForm.email}
                    onChange={(e) => setBookingForm({ ...bookingForm, email: e.target.value })}
                  />
                </div>

                {/* Предпочтительный способ связи */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Способ связи *</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {contactMethods.map((method) => (
                      <label key={method.value} className="flex items-center gap-2 p-2 border rounded cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          name="contact_method"
                          value={method.value}
                          checked={bookingForm.contactMethod === method.value}
                          onChange={() => setBookingForm({ ...bookingForm, contactMethod: method.value })}
                          className="w-4 h-4"
                        />
                        <span className="text-sm">{method.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Дополнительные данные */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ФИО других участников</label>
                  <textarea
                    className="w-full border rounded-lg p-2"
                    rows={2}
                    placeholder="При необходимости"
                    value={bookingForm.participantNames}
                    onChange={(e) => setBookingForm({ ...bookingForm, participantNames: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Комментарий к заявке</label>
                  <textarea
                    className="w-full border rounded-lg p-2"
                    rows={2}
                    placeholder="Дополнительные пожелания"
                    value={bookingForm.comment}
                    onChange={(e) => setBookingForm({ ...bookingForm, comment: e.target.value })}
                  />
                </div>

                {/* Юридическая информация */}
                <div className="space-y-2">
                  {isAuthenticated && (
                    <label className="flex items-start gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        className="w-4 h-4 mt-1"
                        checked={bookingForm.updateProfile}
                        onChange={(e) => setBookingForm({ ...bookingForm, updateProfile: e.target.checked })}
                      />
                      <span className="text-sm text-gray-600">
                        Обновить профиль этими контактными данными
                      </span>
                    </label>
                  )}
                  <label className="flex items-start gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      className="w-4 h-4 mt-1"
                      required
                      checked={bookingForm.personalDataConsent}
                      onChange={(e) => setBookingForm({ ...bookingForm, personalDataConsent: e.target.checked })}
                    />
                    <span className="text-sm text-gray-600">
                      Я согласен на обработку персональных данных в соответствии с{' '}
                      <Link to="/legal/personal-data-policy" className="text-blue-600 hover:underline">политикой конфиденциальности</Link>
                    </span>
                  </label>
                  <label className="flex items-start gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      className="w-4 h-4 mt-1"
                      required
                      checked={bookingForm.offerConsent}
                      onChange={(e) => setBookingForm({ ...bookingForm, offerConsent: e.target.checked })}
                    />
                    <span className="text-sm text-gray-600">
                      Я ознакомлен с{' '}
                      <span className="text-blue-600">договором оферты</span>
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={isBookingSubmitting}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isBookingSubmitting ? 'Создание заказа...' : 'Подтвердить бронирование'}
                </button>
              </form>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
