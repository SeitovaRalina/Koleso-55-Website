import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { excursionsApi } from '../api/excursions'
import { getMediaUrl } from '../utils/media'

const directions = [
  {
    title: 'Экскурсии и путешествия',
    text: 'Знакомим с Омском и Омской областью, организуем поездки по России — для одного человека или группы.',
  },
  {
    title: 'Для детей и школьных групп',
    text: 'Подбираем познавательные экскурсии, поездки и мастер-классы с учётом возраста и интересов участников.',
  },
  {
    title: 'Активные и корпоративные программы',
    text: 'Помогаем провести совместный выезд, активный день или программу для команды.',
  },
]

export default function About() {
  const [ready, setReady] = useState(false)
  const [activeSlide, setActiveSlide] = useState(0)
  const [userPaused, setUserPaused] = useState(false)
  const [interactionPaused, setInteractionPaused] = useState(false)
  const [reducedMotion, setReducedMotion] = useState(false)
  const [failedImages, setFailedImages] = useState<string[]>([])

  // Let the first text paint finish before requesting catalog photos.
  useEffect(() => {
    const timer = window.setTimeout(() => setReady(true), 0)
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const updateMotion = () => setReducedMotion(motion.matches)
    updateMotion()
    motion.addEventListener('change', updateMotion)
    return () => {
      window.clearTimeout(timer)
      motion.removeEventListener('change', updateMotion)
    }
  }, [])

  const { data } = useQuery({
    queryKey: ['about-excursion-photos'],
    queryFn: () => excursionsApi.getExcursions(),
    enabled: ready,
    staleTime: 5 * 60 * 1000,
    retry: false,
  })
  const photos = (data?.results ?? [])
    .map((excursion) => ({ url: getMediaUrl(excursion.main_image), title: excursion.title }))
    .filter((photo): photo is { url: string; title: string } => Boolean(photo.url))
    .filter((photo) => !failedImages.includes(photo.url))
    .slice(0, 9)
  const slides = Array.from({ length: Math.ceil(photos.length / 3) }, (_, index) => photos.slice(index * 3, index * 3 + 3))
  const currentSlide = Math.min(activeSlide, Math.max(slides.length - 1, 0))

  useEffect(() => {
    if (slides.length < 2 || userPaused || interactionPaused || reducedMotion) return
    const timer = window.setInterval(() => {
      if (!document.hidden) setActiveSlide((slide) => (slide + 1) % slides.length)
    }, 6500)
    return () => window.clearInterval(timer)
  }, [slides.length, userPaused, interactionPaused, reducedMotion])

  return (
    <div className='text-neutral-ink'>
      <section
        className='relative isolate overflow-hidden bg-brand-deep py-12 text-white sm:py-16'
        onMouseEnter={() => setInteractionPaused(true)}
        onMouseLeave={() => setInteractionPaused(false)}
        onFocusCapture={() => setInteractionPaused(true)}
        onBlurCapture={(event) => {
          if (!event.currentTarget.contains(event.relatedTarget)) setInteractionPaused(false)
        }}
      >
        {slides[currentSlide] && (
          <div
            key={slides[currentSlide][0].url}
            className='absolute inset-0 -z-20 grid grid-cols-2 gap-1 sm:grid-cols-3'
          >
            {slides[currentSlide].map((photo, photoIndex) => (
              <img
                key={photo.url}
                src={photo.url}
                alt={`Экскурсия «${photo.title}»`}
                className={`h-full w-full object-cover ${photoIndex === 2 ? 'hidden sm:block' : ''}`}
                loading={currentSlide === 0 ? 'eager' : 'lazy'}
                onError={() => setFailedImages((previous) => [...previous, photo.url])}
              />
            ))}
          </div>
        )}
        <div className='absolute inset-0 -z-10 bg-gradient-to-r from-brand-deep/95 via-brand-deep/85 to-brand-deep/70' aria-hidden='true' />
        <div className='mx-auto max-w-content px-4'>
          <p className='text-sm font-semibold uppercase tracking-wider text-white'>О компании</p>
          <h1 className='mt-4 max-w-3xl text-3xl font-bold leading-tight sm:text-5xl'>
            Путешествия, которые подходят именно вам
          </h1>
          <p className='mt-6 max-w-2xl text-base leading-7 text-white sm:text-lg'>
            «Колесо путешествий 55» организует экскурсии и авторские программы по Омску,
            Омской области и России. Мы работаем с частными гостями, школьными группами
            и организациями.
          </p>
          {slides.length > 1 && (
            <div className='mt-8 flex items-center gap-3' aria-label='Фотографии экскурсий'>
              <button type='button' onClick={() => setActiveSlide((currentSlide - 1 + slides.length) % slides.length)} className='rounded-card border border-white/70 px-3 py-2 text-sm font-semibold hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white' aria-label='Предыдущие фотографии'>←</button>
              <span className='text-sm' aria-live='off'>{currentSlide + 1} / {slides.length}</span>
              <button type='button' onClick={() => setActiveSlide((currentSlide + 1) % slides.length)} className='rounded-card border border-white/70 px-3 py-2 text-sm font-semibold hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white' aria-label='Следующие фотографии'>→</button>
              <button type='button' onClick={() => setUserPaused((value) => !value)} className='rounded-card border border-white/70 px-3 py-2 text-sm font-semibold hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white' aria-label={userPaused ? 'Запустить смену фотографий' : 'Остановить смену фотографий'}>{userPaused ? '▶' : 'Ⅱ'}</button>
            </div>
          )}
        </div>
      </section>

      <section className='mx-auto max-w-content px-4 py-12 sm:py-16'>
        <h2 className='text-2xl font-bold sm:text-3xl'>Что мы организуем</h2>
        <div className='mt-8 grid gap-6 md:grid-cols-3'>
          {directions.map(({ title, text }) => (
            <article key={title} className='border-t-2 border-brand-sky pt-5'>
              <h3 className='text-xl font-semibold'>{title}</h3>
              <p className='mt-3 leading-7 text-neutral-text'>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className='bg-brand-mist/50 py-12 sm:py-16'>
        <div className='mx-auto grid max-w-content gap-8 px-4 md:grid-cols-[1fr_auto] md:items-center'>
          <div>
            <h2 className='text-2xl font-bold sm:text-3xl'>Поездка под ваш запрос</h2>
            <p className='mt-4 max-w-2xl leading-7 text-neutral-text'>
              Расскажите, куда хотите отправиться, с кем и в каком формате. Обсудим программу
              и условия. Работаем с физическими и юридическими лицами, оформляем договоры
              и предоставляем отчётные документы.
            </p>
          </div>
          <Link to='/contacts' className='inline-flex min-h-11 items-center justify-center rounded-card bg-brand-deep px-6 py-3 font-semibold text-white hover:bg-brand-sky'>
            Связаться с нами
          </Link>
        </div>
      </section>
    </div>
  )
}
