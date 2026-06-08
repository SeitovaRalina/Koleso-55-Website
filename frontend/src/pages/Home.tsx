import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useMemo, useState, type FormEvent, type ReactNode } from 'react'
import {
  FaArrowRight,
  FaCheck,
  FaEnvelope,
  FaHeadset,
  FaPhone,
  FaRoute,
  FaShieldHalved,
  FaUsers,
  FaWandMagicSparkles,
} from 'react-icons/fa6'
import { excursionsApi } from '../api/excursions'
import { reviewsApi } from '../api/reviews'
import {
  Button,
  EmptyState,
  ErrorState,
  ExcursionCard,
  ImagePlaceholder,
  Input,
  Select,
  Skeleton,
} from '../components/ui'
import { CONTACTS, REVIEW_LINKS } from '../config/contacts'
import type { Excursion, HomepageReview } from '../types'

const locationTypes = [
  { value: 'city', label: 'Городские экскурсии' },
  { value: 'suburban', label: 'Загородные экскурсии' },
  { value: 'russia', label: 'Туры по России' },
]

export default function Home() {
  const navigate = useNavigate()
  const [locationType, setLocationType] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [isDateOpen, setIsDateOpen] = useState(false)

  const today = useMemo(() => toDateInput(new Date()), [])

  const nearestQuery = useQuery({
    queryKey: ['home-nearest-excursions'],
    queryFn: () =>
      excursionsApi.getExcursions({
        page: 1,
        date_from: today,
        ordering: 'created_at',
      }),
    staleTime: 5 * 60 * 1000,
  })

  const homepageReviewsQuery = useQuery({
    queryKey: ['homepage-reviews'],
    queryFn: reviewsApi.getHomepageReviews,
    staleTime: 10 * 60 * 1000,
  })

  const handleSearch = (event: FormEvent) => {
    event.preventDefault()
    const params = new URLSearchParams()
    if (locationType) params.set('location_type', locationType)
    if (dateFrom) params.set('date_from', dateFrom)
    if (dateTo) params.set('date_to', dateTo)
    navigate(`/catalog${params.toString() ? `?${params.toString()}` : ''}`)
  }

  return (
    <div className='bg-[#f4f7fb] text-neutral-ink'>
      <section className='relative min-h-[520px] overflow-hidden bg-neutral-ink text-white md:min-h-[600px]'>
        <img
          src='/hero-bg.jpg'
          alt='Экскурсии по Омску и России'
          className='absolute inset-0 h-full w-full object-cover'
        />
        <div className='absolute inset-0 bg-neutral-ink/50 backdrop-blur-[2px]' />
        <div className='absolute inset-0 bg-gradient-to-r from-neutral-ink/88 via-neutral-ink/58 to-neutral-ink/18' />

        <div className='relative mx-auto flex max-w-content flex-col justify-center px-4 py-14 md:min-h-[600px]'>
          <div className='max-w-2xl'>
            <h1 className='text-4xl font-bold leading-tight md:text-6xl'>
              Открой Омск и Россию по-новому
            </h1>
            <p className='mt-4 max-w-xl text-base leading-7 text-white/92 md:text-lg'>
              Экскурсии, активные туры и мастер-классы. Бронируйте онлайн,
              выбирайте дату и маршрут.
            </p>
          </div>

          <form
            onSubmit={handleSearch}
            className='mt-6 grid max-w-xl gap-3 rounded-card border border-white/30 bg-white p-3 text-neutral-ink shadow-editorial md:grid-cols-[1.2fr_1fr_auto] md:items-center'
          >
            <Select
              value={locationType}
              onChange={event => setLocationType(event.target.value)}
              aria-label='Куда отправиться'
              className='border-transparent bg-[#f3f6fb]'
            >
              <option value=''>Куда отправиться?</option>
              {locationTypes.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>

            <div className='relative'>
              <button
                type='button'
                onClick={() => setIsDateOpen(value => !value)}
                className='h-11 w-full rounded-card border border-transparent bg-[#f3f6fb] px-3 text-left text-sm text-neutral-ink outline-none transition focus:border-brand-sky focus:ring-2 focus:ring-brand-sky/20'
                aria-expanded={isDateOpen}
              >
                {formatDateRangeLabel(dateFrom, dateTo)}
              </button>
              {isDateOpen && (
                <div className='absolute left-0 top-14 z-20 w-full min-w-[280px] rounded-card border border-neutral-line bg-white p-4 shadow-editorial md:w-[360px]'>
                  <div className='grid gap-3 sm:grid-cols-2'>
                    <Input
                      label='Дата'
                      type='date'
                      value={dateFrom}
                      min={today}
                      onChange={event => {
                        setDateFrom(event.target.value)
                        if (dateTo && event.target.value > dateTo) setDateTo('')
                      }}
                    />
                    <Input
                      label='По'
                      type='date'
                      value={dateTo}
                      min={dateFrom || today}
                      onChange={event => setDateTo(event.target.value)}
                    />
                  </div>
                  <div className='mt-4 flex justify-between gap-3'>
                    <Button
                      type='button'
                      variant='ghost'
                      size='sm'
                      onClick={() => {
                        setDateFrom('')
                        setDateTo('')
                      }}
                    >
                      Сбросить
                    </Button>
                    <Button
                      type='button'
                      size='sm'
                      onClick={() => setIsDateOpen(false)}
                    >
                      Готово
                    </Button>
                  </div>
                </div>
              )}
            </div>

            <Button type='submit' className='w-full md:w-auto'>
              Найти
            </Button>
          </form>

          <div className='mt-4'>
            <button
              type='button'
              className='magic-ai-button inline-flex h-12 items-center gap-2 rounded-card border px-5 text-sm font-bold'
              onClick={() => navigate('/recommendations')}
            >
              <FaWandMagicSparkles className='relative z-10 h-5 w-5' aria-hidden='true' />
              <span>Подобрать тур с ИИ</span>
            </button>
          </div>
        </div>
      </section>

      <ExcursionSection title='Ближайшие мероприятия' query={nearestQuery} />

      <section className='bg-[#f4f7fb] py-8 md:py-10'>
        <div className='mx-auto max-w-content px-4'>
          <h2 className='text-3xl font-bold md:text-4xl'>Как это работает</h2>
          <div className='mt-5 grid gap-4 md:grid-cols-3'>
            {[
              [
                '1',
                'Выберите экскурсию',
                'В каталоге есть фильтры по локации, дате, цене и формату маршрута.',
              ],
              [
                '2',
                'Забронируйте и оплатите',
                'Выберите дату, укажите участников и оплатите онлайн. Статус доступен в личном кабинете.',
              ],
              [
                '3',
                'Получите подтверждение',
                'Детали заказа приходят на email, а место закрепляется после успешной оплаты.',
              ],
            ].map(([step, title, text]) => (
              <article
                key={step}
                className='rounded-card border border-neutral-line bg-white p-5 shadow-sm'
              >
                <div className='flex items-start gap-4'>
                  <span className='flex h-11 w-11 shrink-0 items-center justify-center rounded-card bg-brand-mist text-xl font-bold text-brand-deep'>
                    {step}
                  </span>
                  <div>
                    <h3 className='text-base font-bold'>{title}</h3>
                    <p className='mt-2 text-sm leading-6 text-neutral-text'>
                      {text}
                    </p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className='bg-[#f4f7fb] py-8 md:py-10'>
        <div className='mx-auto max-w-content px-4'>
          <h2 className='text-3xl font-bold md:text-4xl'>
            Отзывы наших клиентов
          </h2>
          <div className='mt-5 grid overflow-hidden rounded-card bg-white shadow-sm lg:grid-cols-[1.1fr_1fr]'>
            <ReviewsPanel query={homepageReviewsQuery} />
            <OrganizationPanel />
          </div>
        </div>
      </section>

      <section className='bg-[#e7f0fb] py-9 md:py-10'>
        <div className='mx-auto grid max-w-content items-center gap-8 px-4 lg:grid-cols-[1fr_520px]'>
          <div>
            <h2 className='text-3xl font-bold md:text-4xl'>
              Подарите впечатления
            </h2>
            <p className='mt-2 text-xl font-semibold text-neutral-text'>
              которые запомнятся
            </p>
            <ul className='mt-5 space-y-3 text-sm text-neutral-text'>
              <IconListItem icon={<FaCheck />}>
                Любой номинал: удобно подарить без выбора даты.
              </IconListItem>
              <IconListItem icon={<FaCheck />}>
                Электронный или печатный формат: можно вручить сразу.
              </IconListItem>
              <IconListItem icon={<FaCheck />}>
                Срок действия 12 месяцев: получатель сам выберет маршрут.
              </IconListItem>
            </ul>
            <Button className='mt-6' onClick={() => navigate('/certificates')}>
              Купить сертификат
            </Button>
          </div>
          <img
            src='/certificate.jpg'
            alt='Подарочный сертификат'
            className='w-full rounded-card object-cover'
          />
        </div>
      </section>

      <ContactsSection />
    </div>
  )
}

interface ExcursionSectionProps {
  title: string
  query: {
    data?: { results: Excursion[] }
    isLoading: boolean
    isError: boolean
  }
}

function ExcursionSection({ title, query }: ExcursionSectionProps) {
  const excursions = query.data?.results || []

  return (
    <section className='bg-[#f4f7fb] py-9 md:py-10'>
      <div className='mx-auto max-w-content px-4'>
        <h2 className='text-3xl font-bold md:text-4xl'>{title}</h2>

        {query.isLoading ? (
          <div className='mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4'>
            {Array.from({ length: 8 }, (_, index) => (
              <Skeleton key={index} className='h-[520px]' />
            ))}
          </div>
        ) : query.isError ? (
          <ErrorState title='Не удалось загрузить ближайшие мероприятия' />
        ) : excursions.length === 0 ? (
          <EmptyState
            title='Ближайшие мероприятия не найдены'
            description='Откройте каталог и выберите подходящую дату.'
          />
        ) : (
          <>
            <div className='mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4'>
              {excursions.slice(0, 8).map(excursion => (
                <ExcursionCard
                  key={excursion.id}
                  excursion={excursion}
                  source='direct'
                />
              ))}
            </div>
            <div className='mt-7 flex justify-center'>
              <LinkButton to='/catalog'>
                Открыть весь календарь экскурсий
              </LinkButton>
            </div>
          </>
        )}
      </div>
    </section>
  )
}

function ReviewsPanel({
  query,
}: {
  query: { data?: HomepageReview[]; isLoading: boolean; isError: boolean }
}) {
  const review = query.data?.[0]

  if (query.isLoading) {
    return (
      <div className='p-6'>
        <Skeleton className='h-[500px]' />
      </div>
    )
  }

  if (query.isError || !review) {
    return (
      <article className='p-6'>
        <ImagePlaceholder className='h-72 w-full rounded-card md:h-80' />
        <div className='mt-5 flex items-center justify-between gap-4'>
          <h3 className='font-bold'>Наталья Климон</h3>
          <span className='text-[#f5b400]'>★★★★★</span>
        </div>
        <p className='mt-4 text-sm leading-6 text-neutral-text'>
          Отличная организация, понятный маршрут и живой рассказ. Все прошло
          спокойно, вовремя и с вниманием к группе.
        </p>
      </article>
    )
  }

  return (
    <article className='p-6'>
      {review.main_photo ? (
        <img
          src={review.main_photo}
          alt={review.author_name}
          className='h-72 w-full rounded-card object-cover md:h-80'
        />
      ) : (
        <ImagePlaceholder className='h-72 w-full rounded-card md:h-80' />
      )}
      <div className='mt-5 flex items-center justify-between gap-4'>
        <div>
          <h3 className='font-bold'>{review.author_name}</h3>
          <p className='text-xs text-neutral-text'>{review.excursion_title}</p>
        </div>
        <span className='text-[#f5b400]'>{'★'.repeat(review.rating)}</span>
      </div>
      <p className='mt-4 text-sm leading-6 text-neutral-text'>{review.text}</p>
    </article>
  )
}

function OrganizationPanel() {
  return (
    <aside className='relative flex items-center overflow-hidden bg-gradient-to-br from-brand-mist via-white to-heritage-cream p-8'>
      <div className='absolute right-0 top-0 h-40 w-40 rounded-full bg-nature-green/12 blur-2xl' />
      <div className='absolute bottom-0 left-0 h-44 w-44 rounded-full bg-brand-sky/12 blur-2xl' />
      <div className='relative max-w-sm'>
        <h3 className='text-2xl font-bold'>
          Мы - ассоциация гидов и экскурсоводов из Омска
        </h3>
        <p className='mt-4 text-sm leading-6 text-neutral-text'>
          Создаем живые маршруты: городские прогулки, загородные поездки и туры
          по России.
        </p>
        <ul className='mt-6 space-y-4 text-sm font-semibold text-neutral-text'>
          <IconListItem icon={<FaRoute />}>4 года опыта</IconListItem>
          <IconListItem icon={<FaUsers />}>
            1000+ довольных клиентов
          </IconListItem>
          <IconListItem icon={<FaShieldHalved />}>
            Безопасные онлайн-платежи
          </IconListItem>
          <IconListItem icon={<FaHeadset />}>Поддержка 24/7</IconListItem>
        </ul>
      </div>
    </aside>
  )
}

function ContactsSection() {
  return (
    <section className='bg-white py-10 md:py-12'>
      <div className='mx-auto max-w-content px-4'>
        <div className='rounded-card border border-neutral-line bg-gradient-to-br from-white via-[#f7fbff] to-brand-mist/55 p-6 shadow-sm md:p-8'>
          <div className='grid gap-8 lg:grid-cols-[1fr_1.2fr]'>
            <div>
              <h2 className='mt-2 text-3xl font-bold md:text-4xl'>
                Если у вас остались вопросы, свяжитесь с нами удобным способом
              </h2>
              <p className='mt-4 max-w-xl text-sm leading-6 text-neutral-text'>
                Подскажем маршрут, дату, формат экскурсии и поможем с
                бронированием.
              </p>
            </div>
            <div className='grid gap-4 sm:grid-cols-2'>
              <a
                href={`mailto:${CONTACTS.email}`}
                className='rounded-card border border-neutral-line bg-white p-5 transition hover:border-brand-sky'
              >
                <FaEnvelope className='h-5 w-5 text-brand-deep' aria-hidden='true' />
                <div className='mt-4 text-sm text-neutral-text'>Почта</div>
                <div className='mt-1 font-bold text-brand-deep'>
                  {CONTACTS.email}
                </div>
              </a>
              {CONTACTS.phones.map(phone => (
                <a
                  key={phone.raw}
                  href={`tel:${phone.raw}`}
                  className='rounded-card border border-neutral-line bg-white p-5 transition hover:border-brand-sky'
                >
                  <FaPhone className='h-5 w-5 text-brand-deep' aria-hidden='true' />
                  <div className='mt-4 text-sm text-neutral-text'>
                    {phone.name}
                  </div>
                  <div className='mt-1 font-bold text-brand-deep'>
                    {phone.label}
                  </div>
                </a>
              ))}
            </div>
          </div>

          <div className='mt-8 grid gap-4 border-t border-neutral-line pt-6 md:grid-cols-3'>
            {REVIEW_LINKS.map(link => (
              <a
                key={link.label}
                href={link.href}
                target='_blank'
                rel='noreferrer'
                className='rounded-card bg-white/70 p-4 text-sm transition hover:bg-white'
              >
                <span className='font-bold text-heritage-brick'>
                  {link.label}
                </span>
                <span className='mt-2 block text-neutral-text'>
                  Посмотреть отзывы или написать свой.
                </span>
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

function IconListItem({
  icon,
  children,
}: {
  icon: ReactNode
  children: ReactNode
}) {
  return (
    <li className='flex items-center gap-3'>
      <span className='flex h-8 w-8 shrink-0 items-center justify-center rounded-card bg-white text-brand-deep shadow-sm'>
        {icon}
      </span>
      <span className='leading-6'>{children}</span>
    </li>
  )
}

function LinkButton({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link to={to} className='quiet-link-button'>
      {children}
      <FaArrowRight className='h-4 w-4' aria-hidden='true' />
    </Link>
  )
}

function formatDateRangeLabel(dateFrom: string, dateTo: string) {
  if (dateFrom && dateTo)
    return `${formatDate(dateFrom)} - ${formatDate(dateTo)}`
  if (dateFrom) return formatDate(dateFrom)
  return 'Дата'
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  }).format(new Date(value))
}

function toDateInput(date: Date) {
  return date.toISOString().split('T')[0]
}
