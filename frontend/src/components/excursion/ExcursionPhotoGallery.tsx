import { useEffect, useMemo, useState } from 'react'
import type { ExcursionImage, Review } from '../../types'
import { getMediaUrl } from '../../utils/media'
import { ImagePlaceholder } from '../ui/ImagePlaceholder'
import { cn } from '../ui/utils'

type GalleryTab = 'organizer' | 'traveler'

interface GalleryImage {
  id: string | number
  src: string
  alt: string
}

interface ExcursionPhotoGalleryProps {
  images?: ExcursionImage[]
  reviews?: Review[]
  title: string
}

function resolveImageUrl(path: string | null | undefined): string | null {
  if (!path) return null
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return getMediaUrl(path)
}

function sortOrganizerImages(images: ExcursionImage[]): ExcursionImage[] {
  const mainImage = images.find((image) => image.is_main)
  const otherImages = images.filter((image) => !image.is_main)
  return mainImage ? [mainImage, ...otherImages] : images
}

function buildOrganizerGallery(images: ExcursionImage[], title: string): GalleryImage[] {
  return sortOrganizerImages(images).flatMap((image) => {
    const src = resolveImageUrl(image.image)
    if (!src) return []

    return [{
      id: image.id,
      src,
      alt: image.alt_text || title,
    }]
  })
}

function buildTravelerGallery(reviews: Review[]): GalleryImage[] {
  return reviews.flatMap((review) =>
    (review.images ?? []).flatMap((image) => {
      const src = resolveImageUrl(image.image)
      if (!src) return []

      return [{
        id: `review-${review.id}-${image.id}`,
        src,
        alt: `Фото от ${review.user_name}`,
      }]
    }),
  )
}

function GalleryTile({
  image,
  className,
  overlayLabel,
  onClick,
}: {
  image?: GalleryImage
  className?: string
  overlayLabel?: string
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'relative overflow-hidden rounded-card bg-brand-mist focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-sky',
        className,
      )}
    >
      {image ? (
        <img src={image.src} alt={image.alt} className="h-full w-full object-cover" />
      ) : (
        <ImagePlaceholder className="h-full w-full" />
      )}
      {overlayLabel && (
        <div className="absolute inset-0 flex items-center justify-center bg-neutral-ink/60">
          <span className="text-sm font-semibold text-white">{overlayLabel}</span>
        </div>
      )}
    </button>
  )
}

function Lightbox({
  organizerImages,
  travelerImages,
  activeTab,
  index,
  onTabChange,
  onClose,
  onPrev,
  onNext,
}: {
  organizerImages: GalleryImage[]
  travelerImages: GalleryImage[]
  activeTab: GalleryTab
  index: number
  onTabChange: (tab: GalleryTab) => void
  onClose: () => void
  onPrev: () => void
  onNext: () => void
}) {
  const images = activeTab === 'organizer' ? organizerImages : travelerImages
  const current = images[index]

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
      if (event.key === 'ArrowLeft') onPrev()
      if (event.key === 'ArrowRight') onNext()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose, onNext, onPrev])

  if (!current) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-ink/90 p-4">
      <div className="absolute left-4 top-4 flex max-w-[calc(100%-5rem)] rounded-card bg-white/10 p-1 text-sm font-semibold text-white">
        <button
          type="button"
          onClick={() => onTabChange('organizer')}
          className={cn(
            'rounded-card px-3 py-2 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white',
            activeTab === 'organizer' && 'bg-white text-neutral-ink',
          )}
        >
          Фото организатора
        </button>
        <button
          type="button"
          onClick={() => onTabChange('traveler')}
          disabled={travelerImages.length === 0}
          className={cn(
            'rounded-card px-3 py-2 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white disabled:cursor-not-allowed disabled:opacity-50',
            activeTab === 'traveler' && 'bg-white text-neutral-ink',
          )}
        >
          Фото путешественников
        </button>
      </div>

      <button
        type="button"
        onClick={onClose}
        aria-label="Закрыть галерею"
        className="absolute right-4 top-4 rounded-full bg-white/10 p-2 text-white transition hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
      >
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      {images.length > 1 && (
        <>
          <button
            type="button"
            onClick={onPrev}
            aria-label="Предыдущее фото"
            className="absolute left-4 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-3 text-white transition hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            type="button"
            onClick={onNext}
            aria-label="Следующее фото"
            className="absolute right-4 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-3 text-white transition hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </>
      )}

      <div className="max-h-[85vh] max-w-5xl pt-14 sm:pt-0">
        <img src={current.src} alt={current.alt} className="max-h-[78vh] w-full object-contain sm:max-h-[85vh]" />
        <p className="mt-3 text-center text-sm text-white/80">
          {index + 1} / {images.length}
        </p>
      </div>
    </div>
  )
}

export function ExcursionPhotoGallery({ images = [], reviews = [], title }: ExcursionPhotoGalleryProps) {
  const [previewTab, setPreviewTab] = useState<GalleryTab>('organizer')
  const [activeTab, setActiveTab] = useState<GalleryTab>('organizer')
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null)

  const organizerGallery = useMemo(
    () => buildOrganizerGallery(images, title),
    [images, title],
  )
  const travelerGallery = useMemo(
    () => buildTravelerGallery(reviews),
    [reviews],
  )

  const previewGallery = previewTab === 'organizer' ? organizerGallery : travelerGallery
  const activeGallery = activeTab === 'organizer' ? organizerGallery : travelerGallery
  const visibleImages = previewGallery.slice(0, Math.min(previewGallery.length, 3))
  const hasMorePhotos = previewGallery.length > 3

  const openLightbox = (index: number) => {
    if (previewGallery.length === 0) return
    setActiveTab(previewTab)
    setLightboxIndex(index)
  }

  const closeLightbox = () => setLightboxIndex(null)

  const showPrev = () => {
    if (lightboxIndex === null || activeGallery.length === 0) return
    setLightboxIndex((lightboxIndex - 1 + activeGallery.length) % activeGallery.length)
  }

  const showNext = () => {
    if (lightboxIndex === null || activeGallery.length === 0) return
    setLightboxIndex((lightboxIndex + 1) % activeGallery.length)
  }

  const changePreviewTab = (tab: GalleryTab) => {
    setPreviewTab(tab)
    setActiveTab(tab)
    setLightboxIndex(null)
  }

  const changeLightboxTab = (tab: GalleryTab) => {
    const nextGallery = tab === 'organizer' ? organizerGallery : travelerGallery
    if (nextGallery.length === 0) return
    setActiveTab(tab)
    setLightboxIndex(0)
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2 border-b border-neutral-line">
        <button
          type="button"
          onClick={() => changePreviewTab('organizer')}
          className={cn(
            'min-h-11 rounded-t-card px-4 text-sm font-semibold text-neutral-text transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-sky',
            previewTab === 'organizer' && 'bg-brand-mist text-brand-deep',
          )}
        >
          Фото организатора
        </button>
        <button
          type="button"
          onClick={() => changePreviewTab('traveler')}
          disabled={travelerGallery.length === 0}
          className={cn(
            'min-h-11 rounded-t-card px-4 text-sm font-semibold text-neutral-text transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-sky disabled:cursor-not-allowed disabled:opacity-50',
            previewTab === 'traveler' && 'bg-brand-mist text-brand-deep',
          )}
        >
          Фото путешественников
        </button>
      </div>

      {previewGallery.length === 0 ? (
        <ImagePlaceholder className="aspect-[16/9] w-full rounded-card" />
      ) : previewGallery.length === 1 ? (
        <GalleryTile
          image={previewGallery[0]}
          className="aspect-[4/3] w-full"
          onClick={() => openLightbox(0)}
        />
      ) : previewGallery.length === 2 ? (
        <div className="grid gap-2 sm:grid-cols-2">
          {visibleImages.map((image, index) => (
            <GalleryTile
              key={image.id}
              image={image}
              className="aspect-[3/4] min-h-[260px]"
              onClick={() => openLightbox(index)}
            />
          ))}
        </div>
      ) : (
        <div className="grid h-[280px] grid-cols-1 gap-2 sm:h-[360px] sm:grid-cols-2 lg:h-[420px]">
          {visibleImages.map((image, index) => (
            <GalleryTile
              key={image.id}
              image={image}
              className={cn('h-full min-h-[120px]', index === 0 && 'min-h-[220px] sm:row-span-2')}
              overlayLabel={index === 2 && hasMorePhotos ? 'Смотреть ещё' : undefined}
              onClick={() => openLightbox(index)}
            />
          ))}
        </div>
      )}

      {lightboxIndex !== null && (
        <Lightbox
          organizerImages={organizerGallery}
          travelerImages={travelerGallery}
          activeTab={activeTab}
          index={lightboxIndex}
          onTabChange={changeLightboxTab}
          onClose={closeLightbox}
          onPrev={showPrev}
          onNext={showNext}
        />
      )}
    </div>
  )
}
