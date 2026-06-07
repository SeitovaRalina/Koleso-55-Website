import { useState, type ReactNode } from 'react'
import type { Excursion } from '../types'
import {
  Alert,
  Badge,
  BookingPanel,
  Button,
  Checkbox,
  EmptyState,
  ErrorState,
  ExcursionCard,
  Input,
  Select,
  Skeleton,
  Tabs,
} from '../components/ui'

const colors = [
  { name: 'brand.sky', value: '#0B8ED8', className: 'bg-brand-sky' },
  { name: 'brand.deep', value: '#0A3F9A', className: 'bg-brand-deep' },
  { name: 'brand.mist', value: '#D9EEF7', className: 'bg-brand-mist' },
  { name: 'nature.green', value: '#6FA36B', className: 'bg-nature-green' },
  { name: 'heritage.cream', value: '#F4EFE6', className: 'bg-heritage-cream' },
  { name: 'heritage.brick', value: '#9B4A31', className: 'bg-heritage-brick' },
  { name: 'neutral.ink', value: '#172033', className: 'bg-neutral-ink' },
  { name: 'neutral.text', value: '#4B5563', className: 'bg-neutral-text' },
]

const sampleExcursion: Excursion = {
  id: 55,
  slug: 'omsk-river-stories',
  title: 'Иртыш, крепость и городские легенды',
  short_description: 'Маршрут по историческому центру Омска с камерной группой и живыми историями.',
  category: {
    id: 1,
    name: 'Городская прогулка',
    slug: 'city',
  },
  location_type_display: 'Омск',
  price: '1800',
  duration: 150,
  average_rating: 4.9,
  review_count: 42,
  main_image: '/hero-bg.jpg',
}

export default function UiKit() {
  const [activeTab, setActiveTab] = useState('profile')

  return (
    <div className='bg-neutral-surface text-neutral-ink'>
      <section className='border-b border-neutral-line bg-heritage-cream'>
        <div className='mx-auto max-w-content px-4 py-12 md:py-16'>
          <Badge variant='category'>UI Kit</Badge>
          <div className='mt-5 max-w-3xl'>
            <h1 className='text-4xl font-bold leading-tight md:text-5xl'>
              Дизайн-система для современного travel marketplace
            </h1>
            <p className='mt-4 text-base leading-7 text-neutral-text md:text-lg'>
              База для редизайна страниц: спокойная editorial сетка, продуктовые состояния,
              доступные формы и бизнес-правила бронирования без скрытых условий.
            </p>
          </div>
        </div>
      </section>

      <main className='mx-auto max-w-content px-4 py-10 md:py-14'>
        <UiSection title='Цвета' description='Палитра из hero-bg.jpg: синий как бренд, зеленый и теплые акценты для глубины.'>
          <div className='grid grid-cols-2 gap-4 sm:grid-cols-4'>
            {colors.map(color => (
              <div key={color.name} className='overflow-hidden rounded-card border border-neutral-line bg-white'>
                <div className={`h-24 ${color.className}`} />
                <div className='p-3'>
                  <p className='text-sm font-semibold'>{color.name}</p>
                  <p className='text-xs text-neutral-text'>{color.value}</p>
                </div>
              </div>
            ))}
          </div>
        </UiSection>

        <UiSection title='Типографика' description='Крупный заголовок только для страниц, компактные заголовки для карточек и панелей.'>
          <div className='space-y-4'>
            <div>
              <p className='text-sm text-neutral-text'>Page title</p>
              <p className='text-3xl font-bold md:text-5xl'>Экскурсии по Омску и области</p>
            </div>
            <div>
              <p className='text-sm text-neutral-text'>Section title</p>
              <p className='text-2xl font-bold md:text-3xl'>Ближайшие события недели</p>
            </div>
            <div>
              <p className='text-sm text-neutral-text'>Body</p>
              <p className='max-w-2xl text-base leading-7 text-neutral-text'>
                Текст должен читаться на мобильных экранах, не ломать кнопки и не спорить с фотографией.
              </p>
            </div>
          </div>
        </UiSection>

        <UiSection title='Кнопки и бейджи' description='Высота 44-48 px, radius 8 px, контрастный focus ring.'>
          <div className='flex flex-wrap gap-3'>
            <Button>Основное действие</Button>
            <Button variant='secondary'>Вторичное</Button>
            <Button variant='ghost'>Тихое действие</Button>
            <Button variant='danger'>Отмена</Button>
            <Button variant='icon' aria-label='Поиск'>
              <svg className='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z' />
              </svg>
            </Button>
          </div>
          <div className='mt-5 flex flex-wrap gap-3'>
            <Badge variant='category'>История</Badge>
            <Badge variant='availability'>12 мест</Badge>
            <Badge variant='status'>Ожидает оплаты</Badge>
            <Badge variant='warning'>Цена по запросу</Badge>
            <Badge>Черновик</Badge>
          </div>
        </UiSection>

        <UiSection title='Формы' description='Видимые labels, helper text, ошибки и legal consent без мелкого скрытого текста.'>
          <div className='grid gap-4 md:grid-cols-2'>
            <Input label='Имя' placeholder='Анна' helperText='Как к вам обращаться менеджеру' />
            <Input label='Телефон' placeholder='+7 999 000-00-00' error='Введите телефон для связи' />
            <Select label='Предпочтительный способ связи'>
              <option>Телефон</option>
              <option>Telegram</option>
              <option>Email</option>
            </Select>
            <Input label='Комментарий' placeholder='Пожелания по маршруту' />
          </div>
          <div className='mt-4 grid gap-3 md:grid-cols-2'>
            <Checkbox
              label='Согласие на обработку персональных данных'
              description='Нужно для гостевого бронирования и связи по заказу.'
            />
            <Checkbox
              label='Согласие с условиями бронирования'
              description='Слот занимает место только после успешной оплаты.'
            />
          </div>
        </UiSection>

        <UiSection title='Карточки и состояния' description='Карточка экскурсии, skeleton, empty и error состояния для API-driven экранов.'>
          <div className='grid gap-6 lg:grid-cols-[280px_1fr]'>
            <ExcursionCard excursion={sampleExcursion} source='direct' />
            <div className='grid gap-4'>
              <div className='grid gap-3 sm:grid-cols-3'>
                <Skeleton className='h-24' />
                <Skeleton className='h-24' />
                <Skeleton className='h-24' />
              </div>
              <EmptyState
                title='Экскурсии не найдены'
                description='Попробуйте убрать часть фильтров или выбрать другую дату.'
                actionLabel='Сбросить фильтры'
                onAction={() => undefined}
              />
              <ErrorState onAction={() => undefined} />
            </div>
          </div>
        </UiSection>

        <UiSection title='Бронирование' description='Состояния показывают оплату, manager fallback и правило 48 часов.'>
          <div className='grid gap-5 lg:grid-cols-3'>
            <BookingPanel
              title='Иртыш, крепость и легенды'
              date='14 июня, 12:00'
              seatsLabel='8 из 12'
              priceLabel='1 800 ₽ / чел'
              state='available'
            />
            <BookingPanel
              title='Авторский маршрут'
              date='Дата по согласованию'
              seatsLabel='Индивидуально'
              priceLabel='По запросу'
              state='manager'
            />
            <BookingPanel
              title='Заказ #55'
              date='Оплата получена'
              seatsLabel='2 участника'
              priceLabel='3 600 ₽'
              state='paid'
            />
          </div>
        </UiSection>

        <UiSection title='Tabs и alerts' description='Для кабинета, статусов заказа и backend warnings.'>
          <Tabs
            activeTab={activeTab}
            onChange={setActiveTab}
            tabs={[
              {
                id: 'profile',
                label: 'Профиль',
                content: <Alert title='Email не подтвержден'>Показываем warning, если backend вернул это состояние.</Alert>,
              },
              {
                id: 'orders',
                label: 'Заказы',
                content: <Alert variant='success' title='Оплата прошла'>Заказ стал paid после trusted payment status.</Alert>,
              },
              {
                id: 'refund',
                label: 'Возврат',
                content: <Alert variant='warning' title='До события меньше 48 часов'>Поздняя отмена идет через заявление на возврат.</Alert>,
              },
            ]}
          />
        </UiSection>
      </main>
    </div>
  )
}

interface UiSectionProps {
  title: string
  description: string
  children: ReactNode
}

function UiSection({ title, description, children }: UiSectionProps) {
  return (
    <section className='mb-12 md:mb-16'>
      <div className='mb-5 max-w-2xl'>
        <h2 className='text-2xl font-bold text-neutral-ink md:text-3xl'>{title}</h2>
        <p className='mt-2 text-sm leading-6 text-neutral-text md:text-base'>{description}</p>
      </div>
      {children}
    </section>
  )
}
