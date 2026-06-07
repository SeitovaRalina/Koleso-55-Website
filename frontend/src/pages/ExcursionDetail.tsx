import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { excursionsApi } from '../api/excursions'
import { analyticsApi } from '../api/analytics'
import { wishlistApi } from '../api/wishlist'
import { recommendationsApi } from '../api/recommendations'
import { useAuth } from '../contexts/useAuth'
import type { ExcursionSlot, Review } from '../types'

export default function ExcursionDetail() {
  const { excursionId } = useParams<{ excursionId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated } = useAuth()
  const [selectedSlot, setSelectedSlot] = useState<ExcursionSlot | null>(null)
  const [isFavorite, setIsFavorite] = useState(false)
  const [viewId, setViewId] = useState<number | null>(null)

  const { data: excursion, isLoading, error } = useQuery({
    queryKey: ['excursion', excursionId],
    queryFn: () => excursionsApi.getExcursionById(Number(excursionId!)),
    enabled: !!excursionId,
  })

  const { data: similarExcursions } = useQuery({
    queryKey: ['similar', excursion?.id],
    queryFn: () => recommendationsApi.getSimilarExcursions(excursion!.id),
    enabled: !!excursion?.id,
  })

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
        setViewId(response.view_id)
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
      if (viewId) {
        analyticsApi.endView({ view_id: viewId })
      }
    }
  }, [excursion, isAuthenticated, location.state?.from, location.state?.source, viewId])

  useEffect(() => {
    const heartbeat = setInterval(() => {
      if (viewId) {
        console.log('Sending heartbeat for view:', viewId)
        analyticsApi.heartbeatView({ view_id: viewId, elapsed_seconds: 5 })
          .then(() => console.log('Heartbeat sent successfully'))
          .catch(err => console.error('Heartbeat failed:', err))
      }
    }, 5000)

    return () => clearInterval(heartbeat)
  }, [viewId])

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
    navigate(`/booking/${excursion?.id}/${selectedSlot.id}`)
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              {excursion.images && excursion.images.length > 0 && (
                <div className="relative">
                  <img
                    src={excursion.images.find((img) => img.is_main)?.image || excursion.images[0].image}
                    alt={excursion.title}
                    className="w-full h-96 object-cover"
                  />
                  <button
                    onClick={handleToggleFavorite}
                    className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-md hover:bg-gray-100"
                  >
                    <svg
                      className={`w-6 h-6 ${isFavorite ? 'text-red-500 fill-current' : 'text-gray-400'}`}
                      fill={isFavorite ? 'currentColor' : 'none'}
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                      />
                    </svg>
                  </button>
                </div>
              )}

              <div className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                    {excursion.category.name}
                  </span>
                  <span className="px-3 py-1 bg-gray-100 text-gray-800 text-sm rounded-full">
                    {excursion.location_type_display}
                  </span>
                </div>

                <h1 className="text-3xl font-bold text-gray-900 mb-4">{excursion.title}</h1>

                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span className="ml-1 text-gray-700">{excursion.average_rating || 'Нет оценок'}</span>
                    <span className="ml-1 text-gray-500">({excursion.review_count} отзывов)</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {Math.floor(excursion.duration / 60)}ч {excursion.duration % 60}мин
                  </div>
                </div>

                <div className="text-3xl font-bold text-blue-600 mb-6">
                  от {excursion.price} ₽
                </div>

                <div className="prose max-w-none mb-6">
                  <h3 className="text-lg font-semibold mb-2">Описание</h3>
                  <p className="text-gray-700 whitespace-pre-line">{excursion.description}</p>
                </div>

                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-4">Выберите дату и время</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {excursion.slots?.map((slot) => (
                      <button
                        key={slot.id}
                        onClick={() => setSelectedSlot(slot)}
                        disabled={!slot.is_available}
                        className={`p-4 border rounded-lg text-left transition-colors ${
                          selectedSlot?.id === slot.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        } ${!slot.is_available ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <div className="font-medium">{new Date(slot.date).toLocaleDateString('ru-RU')}</div>
                        <div className="text-gray-600">{slot.time}</div>
                        <div className="text-sm text-gray-500">
                          Осталось мест: {slot.available_seats}/{slot.max_participants}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  onClick={handleBookNow}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Забронировать
                </button>
              </div>
            </div>

            {excursion.approved_reviews && excursion.approved_reviews.length > 0 && (
              <div className="mt-8 bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold mb-4">Отзывы</h3>
                <div className="space-y-4">
                  {excursion.approved_reviews.map((review: Review) => (
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
                          {review.images.map((photo) => (
                            <img key={photo.id} src={photo.image} alt="" className="w-20 h-20 object-cover rounded" />
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            {similarExcursions && similarExcursions.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold mb-4">Похожие экскурсии</h3>
                <div className="space-y-4">
                  {similarExcursions.slice(0, 5).map((rec) => (
                    <Link
                      key={rec.excursion_id}
                      to={`/excursion/${rec.excursion?.slug}`}
                      state={{ source: 'similar' }}
                      className="block group"
                    >
                      <div className="flex gap-3">
                        {rec.excursion?.main_image && (
                          <img
                            src={rec.excursion.main_image}
                            alt={rec.excursion.title}
                            className="w-24 h-24 object-cover rounded"
                          />
                        )}
                        <div className="flex-1">
                          <h4 className="font-medium group-hover:text-blue-600 transition-colors">
                            {rec.excursion?.title}
                          </h4>
                          <p className="text-sm text-gray-600">{rec.excursion?.short_description}</p>
                          <p className="text-blue-600 font-medium mt-1">
                            от {rec.excursion?.price} ₽
                          </p>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
