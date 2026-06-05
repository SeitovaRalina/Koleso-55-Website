import { useQuery } from '@tanstack/react-query'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import ExcursionCard from '../ExcursionCard'
import { excursionsApi } from '../../api/excursions'
import type { Excursion } from '../../types'

export default function WeeklyEvents() {
  // Вычисляем даты: сегодня + 7 дней
  const today = new Date()
  const nextWeek = new Date()
  nextWeek.setDate(today.getDate() + 7)

  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0]
  }

  const {
    data: excursionsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['weekly-excursions'],
    queryFn: () => excursionsApi.getExcursions({
      page: 1,
      date_from: formatDate(today),
      date_to: formatDate(nextWeek),
    }),
    staleTime: 5 * 60 * 1000,
  })

  const excursions = excursionsData?.results || []

  return (
    <section className='py-16 px-4 bg-gray-50'>
      <div className='max-w-6xl mx-auto'>
        <h2 className='text-3xl font-bold mb-8'>Экскурсии недели</h2>

        {isLoading ? (
          <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6'>
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className='bg-gray-200 rounded-xl h-96 animate-pulse'
              />
            ))}
          </div>
        ) : error ? (
          <div className='text-center py-12'>
            <p className='text-gray-600'>Ошибка загрузки экскурсий</p>
          </div>
        ) : excursions.length === 0 ? (
          <div className='text-center py-12'>
            <p className='text-gray-600'>Экскурсии не найдены</p>
          </div>
        ) : (
          <Swiper
            modules={[Navigation]}
            spaceBetween={24}
            slidesPerView={1}
            navigation
            breakpoints={{
              640: { slidesPerView: 2 },
              1024: { slidesPerView: 3 },
              1280: { slidesPerView: 4 },
            }}
            className='pb-12'
          >
            {excursions.slice(0, 8).map((excursion: Excursion) => (
              <SwiperSlide key={excursion.id}>
                <ExcursionCard excursion={excursion} />
              </SwiperSlide>
            ))}
          </Swiper>
        )}
      </div>
    </section>
  )
}
