import { Link } from 'react-router-dom'
import type { Excursion } from '../types'

interface ExcursionCardProps {
  excursion: Excursion
  source?: 'search' | 'catalog' | 'recommendation' | 'similar' | 'direct'
}

export default function ExcursionCard({ excursion, source = 'direct' }: ExcursionCardProps) {
  const imageUrl = excursion.main_image || '/placeholder.jpg'
  const categoryName = excursion.category?.name || 'Экскурсия'

  return (
    <Link to={`/excursion/${excursion.id}`} state={{ source }} className='group block'>
      <div className='bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow'>
        <div className='relative aspect-[3/4] overflow-hidden'>
          <img
            src={imageUrl}
            alt={excursion.title}
            className='w-full h-full object-cover group-hover:scale-105 transition-transform duration-300'
          />
          <div className='absolute top-3 left-3'>
            <span className='bg-primary text-white text-xs font-medium px-3 py-1 rounded-full'>
              {categoryName}
            </span>
          </div>
          <button className='absolute top-3 right-3 bg-white/90 backdrop-blur-sm p-2 rounded-full hover:bg-white transition-colors'>
            <svg
              className='w-5 h-5 text-gray-600'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'
              />
            </svg>
          </button>
        </div>

        <div className='p-4'>
          <h3 className='font-semibold text-gray-900 mb-2 line-clamp-2'>
            {excursion.title}
          </h3>
          <p className='text-sm text-gray-600 mb-3 line-clamp-2'>
            {excursion.short_description || excursion.description}
          </p>

          <div className='flex items-center justify-between'>
            <div>
              <span className='text-lg font-bold text-primary'>
                {excursion.price} ₽
              </span>
              <span className='text-sm text-gray-500'>/чел</span>
            </div>
            <div className='flex items-center gap-1 text-sm text-gray-600'>
              <svg
                className='w-4 h-4 text-yellow-400'
                fill='currentColor'
                viewBox='0 0 20 20'
              >
                <path d='M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z' />
              </svg>
              <span>{excursion.average_rating || '-'}</span>
              <span className='text-gray-400'>({excursion.review_count})</span>
            </div>
          </div>

          <div className='flex items-center gap-2 mt-3 text-sm text-gray-500'>
            <svg
              className='w-4 h-4'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
              />
            </svg>
            <span>{excursion.duration} мин</span>
          </div>
        </div>
      </div>
    </Link>
  )
}
