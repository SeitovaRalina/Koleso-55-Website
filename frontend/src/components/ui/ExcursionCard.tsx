import { useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { wishlistApi } from '../../api/wishlist'
import type { Excursion, ExcursionSlot } from '../../types'
import { Badge } from './Badge'

interface ExcursionCardProps {
  excursion: Excursion
  source?: 'search' | 'catalog' | 'recommendation' | 'similar' | 'direct'
  compact?: boolean
}

function formatDuration(minutes: number) {
  if (minutes < 60) return `${minutes} мин`
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return rest ? `${hours} ч ${rest} мин` : `${hours} ч`
}

function formatShortDate(value: string) {
  return new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: '2-digit' }).format(new Date(value))
}

function getSlotBadge(slots?: ExcursionSlot[]) {
  const availableSlots = slots?.filter(slot => slot.is_available) || []
  const nearestSlot = availableSlots[0] || slots?.[0]

  if (!nearestSlot) return null

  const seats = nearestSlot.available_seats
  const firstDate = formatShortDate(nearestSlot.date)
  const endDateValue = nearestSlot.date_to || nearestSlot.end_date
  const endDate = endDateValue && endDateValue !== nearestSlot.date ? formatShortDate(endDateValue) : null

  return {
    seats,
    dateLine: endDate ? `${firstDate} - ${endDate}` : `${firstDate}, ${nearestSlot.time.slice(0, 5)}`,
  }
}

export function ExcursionCard({ excursion, source = 'direct' }: ExcursionCardProps) {
  const imageUrl = excursion.main_image || '/hero-bg.jpg'
  const categoryName = excursion.category?.name || 'Экскурсия'
  const slotBadge = getSlotBadge(excursion.nearest_slots)
  const favoriteMutation = useMutation({
    mutationFn: () => wishlistApi.addToWishlist(excursion.id),
  })

  return (
    <article className='group overflow-hidden rounded-card border border-neutral-line bg-white shadow-sm transition hover:shadow-editorial'>
      <Link to={`/excursion/${excursion.id}`} state={{ source }} className='block'>
        <div className='relative aspect-[3/4] overflow-hidden bg-brand-mist'>
          <img
            src={imageUrl}
            alt={excursion.title}
            className='h-full w-full object-cover transition duration-500 group-hover:scale-105'
          />
          <div className='absolute left-3 top-3'>
            <Badge variant='category'>{categoryName}</Badge>
          </div>
          <div className='absolute right-3 top-3'>
            <button
              type='button'
              aria-label='Добавить в избранное'
              className='flex h-10 w-10 items-center justify-center rounded-full bg-transparent text-brand-deep transition hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-deep disabled:cursor-not-allowed disabled:opacity-60'
              disabled={favoriteMutation.isPending}
              onClick={event => {
                event.preventDefault()
                event.stopPropagation()
                favoriteMutation.mutate()
              }}
            >
              <img
                src={favoriteMutation.isSuccess ? '/icons/like-active-icon.svg' : '/icons/like-icon.svg'}
                alt=''
                className='h-7 w-7 drop-shadow'
              />
            </button>
          </div>
          {slotBadge && (
            <div className='absolute bottom-3 left-3 max-w-[calc(100%-24px)] rounded-card bg-neutral-ink/84 px-3 py-2 text-xs font-bold leading-5 text-white shadow-sm backdrop-blur'>
              <div>Осталось {slotBadge.seats} мест</div>
              <div>{slotBadge.dateLine}</div>
            </div>
          )}
        </div>
      </Link>

      <div className='p-4'>
        <Link to={`/excursion/${excursion.id}`} state={{ source }} className='block'>
          <h3 className='line-clamp-2 text-base font-semibold text-neutral-ink transition group-hover:text-brand-deep'>
            {excursion.title}
          </h3>
        </Link>
        <p className='mt-2 line-clamp-2 text-sm text-neutral-text'>
          {excursion.short_description || excursion.description || 'Маршрут, детали и свободные даты внутри.'}
        </p>

        <div className='mt-4 flex items-end justify-between gap-3'>
          <div>
            <p className='text-xs text-neutral-text'>от</p>
            <p className='text-lg font-bold text-brand-deep'>{excursion.price} ₽</p>
          </div>
          <div className='text-right text-sm text-neutral-text'>
            <p>{formatDuration(excursion.duration)}</p>
            <p aria-label='Рейтинг'>
              ★ {excursion.average_rating ?? '-'} <span className='text-neutral-text/70'>({excursion.review_count})</span>
            </p>
          </div>
        </div>
      </div>
    </article>
  )
}

export default ExcursionCard
