import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

const reviews = [
  {
    name: 'Анна Петрова',
    rating: 5,
    comment:
      'Прекрасная экскурсия по Омску! Гид очень знающий и увлекательный рассказчик. Рекомендую всем!',
    date: '15 мая 2024',
  },
  {
    name: 'Михаил Иванов',
    rating: 5,
    comment:
      'Отлично организованная поездка в Тару. Всё прошло по расписанию, впечатления незабываемые.',
    date: '10 мая 2024',
  },
  {
    name: 'Елена Сидорова',
    rating: 4,
    comment:
      'Хорошая экскурсия, но хотелось бы больше времени на фотосессию. В остальном всё отлично.',
    date: '5 мая 2024',
  },
  {
    name: 'Дмитрий Козлов',
    rating: 5,
    comment:
      'Впервые в Омске и экскурсия помогла узнать город с новой стороны. Большое спасибо!',
    date: '28 апреля 2024',
  },
]

export default function Reviews() {
  return (
    <section className='py-16 px-4 bg-white'>
      <div className='max-w-6xl mx-auto'>
        <h2 className='text-3xl font-bold text-center mb-12'>
          Отзывы наших гостей
        </h2>

        <div className='relative'>
          <Swiper
            modules={[Navigation, Pagination]}
            spaceBetween={24}
            slidesPerView={1}
            navigation={{
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
            }}
            pagination={{
              clickable: true,
              el: '.swiper-pagination',
            }}
            breakpoints={{
              640: { slidesPerView: 2 },
              1024: { slidesPerView: 3 },
            }}
            className='pb-16'
          >
            {reviews.map((review, index) => (
              <SwiperSlide key={index}>
                <div className='bg-gray-50 rounded-xl p-6 h-full'>
                  <div className='flex items-center gap-1 mb-3'>
                    {[...Array(5)].map((_, i) => (
                      <svg
                        key={i}
                        className={`w-5 h-5 ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}`}
                        fill='currentColor'
                        viewBox='0 0 20 20'
                      >
                        <path d='M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z' />
                      </svg>
                    ))}
                  </div>
                  <p className='text-gray-700 mb-4'>"{review.comment}"</p>
                  <div className='flex items-center justify-between'>
                    <span className='font-semibold text-gray-900'>
                      {review.name}
                    </span>
                    <span className='text-sm text-gray-500'>{review.date}</span>
                  </div>
                </div>
              </SwiperSlide>
            ))}
          </Swiper>

          <button className='swiper-button-prev absolute top-1/2 left-0 -translate-y-1/2 z-10 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors -translate-x-1/2'>
            <svg
              className='w-6 h-6 text-gray-600'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M15 19l-7-7 7-7'
              />
            </svg>
          </button>

          <button className='swiper-button-next absolute top-1/2 right-0 -translate-y-1/2 z-10 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors translate-x-1/2'>
            <svg
              className='w-6 h-6 text-gray-600'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M9 5l7 7-7 7'
              />
            </svg>
          </button>

          <div className='swiper-pagination absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2'></div>
        </div>
      </div>
    </section>
  )
}
