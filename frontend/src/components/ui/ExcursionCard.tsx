import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { wishlistApi } from '../../api/wishlist'
import { getMediaUrl } from '../../utils/media'
import type { Excursion, ExcursionSlot } from '../../types'
import { Badge } from './Badge'
import { FavoriteIcon } from './FavoriteIcon'
import { ImagePlaceholder } from './ImagePlaceholder'
import { useAuth } from '../../contexts/useAuth'
import { formatDuration, formatSlot, getPrice } from '../../utils/excursionDisplay'

interface ExcursionCardProps {
  excursion: Excursion
  source?: 'search' | 'catalog' | 'recommendation' | 'similar' | 'direct' | 'wishlist'
  compact?: boolean
}

function getSlotBadge(slots?: ExcursionSlot[], multiDay = false) {
  const availableSlots = slots?.filter(slot => slot.is_available) || []
  const nearestSlot = availableSlots[0] || slots?.[0]

  if (!nearestSlot) return null

  const seats = nearestSlot.available_seats
  return {
    seats,
    slot: nearestSlot,
    dateLine: formatSlot(nearestSlot, true, multiDay),
  }
}

export function ExcursionCard({ excursion, source = 'direct' }: ExcursionCardProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuth()
  const imageUrl = getMediaUrl(excursion.main_image)
  const categoryName = excursion.category?.name || 'Экскурсия'
  const slotBadge = getSlotBadge(excursion.nearest_slots, excursion.is_multi_day)
  const price = getPrice(excursion, slotBadge?.slot)
  
  // Check initial wishlist status
  const { data: wishlistCheck } = useQuery({
    queryKey: ['wishlist-check', excursion.id],
    queryFn: () => wishlistApi.checkInWishlist(excursion.id),
    enabled: isAuthenticated,
  })

  const isFavorite = wishlistCheck?.is_in_wishlist ?? false

  const favoriteMutation = useMutation({
    mutationFn: () =>
      isFavorite
        ? wishlistApi.removeFromWishlist(excursion.id)
        : wishlistApi.addToWishlist(excursion.id),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ['wishlist-check', excursion.id] })
      const previous = queryClient.getQueryData<{ is_in_wishlist: boolean }>([
        'wishlist-check',
        excursion.id,
      ])
      queryClient.setQueryData(['wishlist-check', excursion.id], {
        is_in_wishlist: !isFavorite,
      })
      return { previous }
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['wishlist-check', excursion.id], context.previous)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] })
      queryClient.invalidateQueries({ queryKey: ['wishlist-check', excursion.id] })
    },
  })

  const handleFavoriteClick = (event: React.MouseEvent) => {
    event.preventDefault()
    event.stopPropagation()
    
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    
    favoriteMutation.mutate()
  }

  return (
    <article className='group overflow-hidden rounded-card border border-neutral-line bg-white shadow-sm transition hover:shadow-editorial'>
      <Link to={`/excursion/${excursion.id}`} state={{ source }} className='block'>
        <div className='relative aspect-[3/4] overflow-hidden bg-brand-mist'>
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={excursion.title}
              className='h-full w-full object-cover transition duration-500 group-hover:scale-105'
            />
          ) : (
            <ImagePlaceholder className='h-full w-full' />
          )}
          <div className='absolute left-3 top-3'>
            <Badge variant='category'>{categoryName}</Badge>
          </div>
          <div className='absolute right-3 top-3'>
            <button
              type='button'
              aria-label={isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'}
              className='flex h-10 w-10 items-center justify-center rounded-full bg-transparent transition hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-deep disabled:cursor-not-allowed disabled:opacity-60'
              disabled={favoriteMutation.isPending}
              onClick={handleFavoriteClick}
            >
              <FavoriteIcon active={isFavorite} className='h-7 w-7 drop-shadow' />
            </button>
          </div>
          {slotBadge && (
            <div className='absolute bottom-3 left-3 max-w-[calc(100%-24px)] rounded-card bg-neutral-ink/90 px-3 py-2 text-xs font-bold leading-5 text-white shadow-sm'>
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
            {price.from && <p className='text-xs text-neutral-text'>от</p>}
            <p className='text-lg font-bold text-brand-deep'>{price.amount} ₽</p>
          </div>
          <div className='text-right text-sm text-neutral-text'>
            <p>{formatDuration(excursion, slotBadge?.slot)}</p>
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
