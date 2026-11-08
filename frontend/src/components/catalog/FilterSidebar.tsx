import { useEffect, useState, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { excursionsApi } from '../../api/excursions'

export interface FilterState {
  categories: string[]
  locations: string[]
  durations: string[]
  minPrice: string
  maxPrice: string
  dateFrom: string
  dateTo: string
}

interface Props {
  filters: FilterState
  onFiltersChange: (filters: FilterState) => void
  onResetAll: () => void
  open: boolean
  onClose: () => void
}

const locations = [
  { value: 'city', label: 'Городские экскурсии' },
  { value: 'suburban', label: 'Загородные экскурсии' },
  { value: 'russia', label: 'Туры по России' },
]
const durations = [
  { value: 'under_2h', label: 'До 2 часов' },
  { value: '2_to_4h', label: 'От 2 до 4 часов' },
  { value: 'over_4h', label: 'Более 4 часов' },
]
type Section = 'categories' | 'price' | 'locations' | 'durations' | 'date'
const titles: Record<Section, string> = { categories: 'Категории', price: 'Цена', locations: 'Локация', durations: 'Длительность', date: 'Дата' }

export default function FilterSidebar({ filters, onFiltersChange, onResetAll, open, onClose }: Props) {
  const [expanded, setExpanded] = useState<Record<Section, boolean>>({ categories: true, price: true, locations: true, durations: true, date: true })
  const [allCategories, setAllCategories] = useState(false)
  const [categorySearch, setCategorySearch] = useState('')
  const { data: categories = [], isLoading } = useQuery({ queryKey: ['categories'], queryFn: excursionsApi.getCategories, staleTime: 600000 })

  useEffect(() => {
    if (!open) return
    const escape = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    window.addEventListener('keydown', escape)
    return () => window.removeEventListener('keydown', escape)
  }, [open, onClose])

  const change = (patch: Partial<FilterState>) => onFiltersChange({ ...filters, ...patch })
  const resetCategories = () => {
    setCategorySearch('')
    setAllCategories(false)
    change({ categories: [] })
  }
  const resetAll = () => {
    setCategorySearch('')
    setAllCategories(false)
    onResetAll()
  }
  const toggle = (key: 'categories' | 'locations' | 'durations', value: string) => {
    const selected = filters[key]
    const next = selected.includes(value) ? selected.filter(item => item !== value) : [...selected.filter(Boolean), value]
    change({ [key]: key === 'categories' && next.length === 0 ? [''] : next })
  }
  const count = (section: Section) => {
    if (section === 'categories') return filters.categories.filter(Boolean).length
    if (section === 'locations') return filters.locations.length
    if (section === 'durations') return filters.durations.length
    if (section === 'price') return Number(Boolean(filters.minPrice)) + Number(Boolean(filters.maxPrice))
    return Number(Boolean(filters.dateFrom)) + Number(Boolean(filters.dateTo))
  }
  const section = (key: Section, children: ReactNode) => (
    <section key={key} className='border-t border-gray-200 py-3'>
      <div className='flex items-center gap-2'>
        <button type='button' aria-expanded={expanded[key]} onClick={() => setExpanded({ ...expanded, [key]: !expanded[key] })}
          className={`flex-1 text-left font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary ${count(key) ? 'text-primary' : 'text-gray-800'}`}>
          {titles[key]} {count(key) > 0 && <span className='text-xs rounded-full bg-blue-50 px-2 py-1'>{count(key)}</span>}
          <span aria-hidden='true' className='float-right'>{expanded[key] ? '−' : '+'}</span>
        </button>
        {(count(key) > 0 || (key === 'categories' && filters.categories.length > 0)) && <button type='button' onClick={() => key === 'categories' ? resetCategories() : change(key === 'locations' ? { locations: [] } : key === 'durations' ? { durations: [] } : key === 'price' ? { minPrice: '', maxPrice: '' } : { dateFrom: '', dateTo: '' })} className='text-xs text-primary underline focus-visible:outline'>Сбросить</button>}
      </div>
      {expanded[key] && <div className='mt-3'>{children}</div>}
    </section>
  )
  const searched = categories.filter(cat => cat.name.toLowerCase().includes(categorySearch.toLowerCase()))
  const shown = allCategories || categorySearch ? searched : searched.slice(0, 6)
  const checkbox = (key: 'categories' | 'locations' | 'durations', value: string, label: string) => (
    <label key={value} className='flex items-start gap-2 py-1 cursor-pointer text-sm text-gray-700'>
      <input type='checkbox' checked={filters[key].includes(value)} onChange={() => toggle(key, value)} className='mt-1 accent-blue-600 focus-visible:outline' />
      <span>{label}</span>
    </label>
  )
  return (
    <aside className={`${open ? 'block' : 'hidden'} lg:block w-full lg:w-64 shrink-0`} aria-label='Фильтры каталога'>
      <div className='bg-white border border-gray-200 rounded-lg p-4'>
        <div className='flex justify-between items-center mb-3'>
          <h2 className='text-lg font-bold'>Фильтры</h2>
          <button type='button' onClick={onClose} className='lg:hidden text-primary focus-visible:outline' aria-label='Закрыть фильтры'>Закрыть</button>
        </div>
        <button type='button' onClick={resetAll} className='text-sm text-primary underline mb-2 focus-visible:outline'>Сбросить все фильтры</button>
        {section('categories', <>
          <button type='button' onClick={resetCategories} className='block text-sm text-primary mb-2 focus-visible:outline'>Все категории</button>
          {categories.length > 6 && <input type='search' aria-label='Поиск категории' placeholder='Найти категорию' value={categorySearch} onChange={event => setCategorySearch(event.target.value)} className='w-full min-w-0 border rounded px-2 py-2 mb-2 focus-visible:outline-primary' />}
          <div className={allCategories || categorySearch ? 'max-h-52 overflow-y-auto' : ''}>
            {isLoading ? <p>Загрузка категорий…</p> : shown.length ? shown.map(cat => checkbox('categories', cat.slug, cat.name)) : <p className='text-sm text-gray-500'>Категории не найдены</p>}
          </div>
          {categories.length > 6 && !categorySearch && <button type='button' onClick={() => setAllCategories(!allCategories)} className='text-sm text-primary mt-2 focus-visible:outline'>{allCategories ? 'Свернуть' : 'Показать все'}</button>}
        </>)}
        {section('price', <div className='grid grid-cols-2 gap-2'>
          <label className='text-xs min-w-0'>От, ₽<input type='number' min='0' value={filters.minPrice} onChange={e => change({ minPrice: e.target.value })} className='w-full min-w-0 border rounded px-2 py-2 focus-visible:outline-primary' /></label>
          <label className='text-xs min-w-0'>До, ₽<input type='number' min='0' value={filters.maxPrice} onChange={e => change({ maxPrice: e.target.value })} className='w-full min-w-0 border rounded px-2 py-2 focus-visible:outline-primary' /></label>
        </div>)}
        {section('locations', locations.map(loc => checkbox('locations', loc.value, loc.label)))}
        {section('durations', durations.map(dur => checkbox('durations', dur.value, dur.label)))}
        {section('date', <>
          <div className='grid grid-cols-2 gap-2'>
            <label className='text-xs min-w-0'>От<input type='date' value={filters.dateFrom} onChange={e => change({ dateFrom: e.target.value })} className='w-full min-w-0 border rounded px-1 py-2 text-xs focus-visible:outline-primary' /></label>
            <label className='text-xs min-w-0'>До<input type='date' value={filters.dateTo} onChange={e => change({ dateTo: e.target.value })} className='w-full min-w-0 border rounded px-1 py-2 text-xs focus-visible:outline-primary' /></label>
          </div>
          {filters.dateFrom && filters.dateTo && filters.dateFrom > filters.dateTo && <p role='alert' className='text-sm text-red-700 mt-2'>Дата «От» позже даты «До»</p>}
        </>)}
      </div>
    </aside>
  )
}
