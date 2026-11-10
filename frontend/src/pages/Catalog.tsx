import { useState, useEffect, useRef, type FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import FilterSidebar, { type FilterState } from '../components/catalog/FilterSidebar'
import ExcursionCard from '../components/ExcursionCard'
import { excursionsApi } from '../api/excursions'

const ordering: Record<string, string> = { popular: '-created_at', price_asc: 'price', price_desc: '-price', duration: 'duration', newest: '-created_at' }
function readFilters(params: URLSearchParams): FilterState {
  return {
    categories: params.getAll('category'), locations: params.getAll('location_type'), durations: params.getAll('duration'),
    minPrice: params.get('min_price') || '', maxPrice: params.get('max_price') || '',
    dateFrom: params.get('date_from') || '', dateTo: params.get('date_to') || '',
  }
}

function getPaginationItems(currentPage: number, totalPages: number): Array<number | 'ellipsis'> {
  const pages = new Set([1, totalPages, currentPage - 1, currentPage, currentPage + 1])
  const sorted = [...pages].filter(page => page >= 1 && page <= totalPages).sort((a, b) => a - b)

  return sorted.flatMap((page, index) => {
    const previous = sorted[index - 1]
    return previous && page - previous > 1 ? ['ellipsis' as const, page] : [page]
  })
}

export default function Catalog() {
  const [params, setParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState(params.get('search') || '')
  const [open, setOpen] = useState(false)
  const [desktopVisible, setDesktopVisible] = useState(true)
  const resultControlsRef = useRef<HTMLDivElement>(null)
  const shouldScrollToResults = useRef(false)
  const filters = readFilters(params)
  const page = Math.max(1, Number(params.get('page')) || 1)
  const sort = Object.keys(ordering).find(key => key !== 'popular' && ordering[key] === params.get('ordering')) || 'popular'
  const invalidDate = Boolean(filters.dateFrom && filters.dateTo && filters.dateFrom > filters.dateTo)
  const noCategories = params.has('category') && filters.categories.some(value => !value)
  const invalidPrice = Boolean(filters.minPrice && filters.maxPrice && Number(filters.minPrice) > Number(filters.maxPrice))

  useEffect(() => {
    const onHistory = () => setSearchQuery(new URLSearchParams(window.location.search).get('search') || '')
    window.addEventListener('popstate', onHistory)
    return () => window.removeEventListener('popstate', onHistory)
  }, [])

  const update = (patch: (next: URLSearchParams) => void, resetPage = true) => {
    const next = new URLSearchParams(params)
    patch(next)
    if (resetPage) next.delete('page')
    setParams(next)
  }
  const handleFiltersChange = (value: FilterState) => update(next => {
    for (const key of ['category', 'location_type', 'duration', 'min_price', 'max_price', 'date_from', 'date_to']) next.delete(key)
    value.categories.forEach(item => next.append('category', item))
    value.locations.forEach(item => next.append('location_type', item))
    value.durations.forEach(item => next.append('duration', item))
    if (value.minPrice) next.set('min_price', value.minPrice)
    if (value.maxPrice) next.set('max_price', value.maxPrice)
    if (value.dateFrom) next.set('date_from', value.dateFrom)
    if (value.dateTo) next.set('date_to', value.dateTo)
  })
  const resetAllFilters = () => {
    setSearchQuery('')
    setParams(new URLSearchParams())
  }
  const { data, isLoading, error } = useQuery({
    queryKey: ['excursions', params.toString()],
    queryFn: () => excursionsApi.getExcursions({
      page, category: filters.categories, location_type: filters.locations, duration: filters.durations,
      min_price: filters.minPrice ? Number(filters.minPrice) : undefined,
      max_price: filters.maxPrice ? Number(filters.maxPrice) : undefined,
      date_from: filters.dateFrom || undefined, date_to: filters.dateTo || undefined,
      search: params.get('search') || undefined, ordering: params.get('ordering') || '-created_at',
    }),
    enabled: !invalidDate && !noCategories && !invalidPrice,
    staleTime: 300000,
  })
  const totalPages = Math.ceil((data?.count || 0) / 12)
  const paginationItems = getPaginationItems(page, totalPages)

  useEffect(() => {
    if (!shouldScrollToResults.current || isLoading) return
    resultControlsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    shouldScrollToResults.current = false
  }, [isLoading, data?.results])

  const goToPage = (targetPage: number) => {
    if (targetPage === page) return
    shouldScrollToResults.current = true
    update(next => next.set('page', String(targetPage)), false)
  }
  const submitSearch = (event: FormEvent) => {
    event.preventDefault()
    update(next => { if (searchQuery.trim()) next.set('search', searchQuery.trim()); else next.delete('search') })
  }
  return <main className='max-w-6xl mx-auto px-4 py-8'>
    <div className='mb-5 flex flex-wrap items-center gap-3'>
      <h1 className='text-2xl font-bold flex-1 min-w-48'>Каталог экскурсий</h1>
      <button type='button' aria-expanded={desktopVisible} onClick={() => setDesktopVisible(!desktopVisible)} className='hidden lg:block border rounded px-4 py-2 text-primary focus-visible:outline-primary'>{desktopVisible ? 'Скрыть фильтры' : 'Показать фильтры'}</button>
      <button type='button' aria-expanded={open} onClick={() => setOpen(!open)} className='lg:hidden border rounded px-4 py-2 text-primary focus-visible:outline-primary'>Фильтры</button>
    </div>
    <div className='flex flex-col lg:flex-row gap-8'>
      {(desktopVisible || open) && <div className={desktopVisible ? '' : 'lg:hidden'}><FilterSidebar filters={filters} onFiltersChange={handleFiltersChange} onResetAll={resetAllFilters} open={open} onClose={() => setOpen(false)} /></div>}
      <div className='min-w-0 flex-1'>
        <form onSubmit={submitSearch} className='flex flex-wrap gap-2 mb-5'>
          <label htmlFor='catalog-search' className='sr-only'>Поиск экскурсий</label>
          <input id='catalog-search' type='search' value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder='Поиск экскурсий' className='flex-1 min-w-40 border rounded px-3 py-2 focus-visible:outline-primary' />
          <button type='submit' className='bg-primary text-white rounded px-4 py-2 focus-visible:outline-primary'>Найти</button>
        </form>
        <div ref={resultControlsRef} className='flex flex-wrap items-center justify-between gap-3 mb-5 scroll-mt-24'>
          <p aria-live='polite' className='text-gray-600'>Найдено {invalidDate || noCategories || invalidPrice ? 0 : data?.count || 0} экскурсий</p>
          <label className='text-sm'>Сортировка <select value={sort} onChange={e => update(next => { if (e.target.value === 'popular') next.delete('ordering'); else next.set('ordering', ordering[e.target.value]) })} className='ml-2 border rounded px-2 py-2 focus-visible:outline-primary'>
            <option value='popular'>По популярности</option><option value='price_asc'>Цена: по возрастанию</option><option value='price_desc'>Цена: по убыванию</option><option value='duration'>По длительности</option><option value='newest'>Сначала новые</option>
          </select></label>
        </div>
        {invalidDate || invalidPrice ? <p role='alert' className='text-red-700 py-8'>Проверьте диапазон {invalidDate ? 'дат' : 'цены'}: начало позже конца.</p>
          : noCategories ? <p className='py-8'>Выберите категорию или нажмите «Все категории».</p>
          : isLoading ? <div className={`grid grid-cols-1 sm:grid-cols-2 ${desktopVisible ? 'xl:grid-cols-3' : 'xl:grid-cols-4'} gap-6`}>{Array.from({ length: 6 }, (_, i) => <div key={i} className='bg-gray-100 h-96 animate-pulse rounded' />)}</div>
          : error ? <p role='alert' className='py-8'>Не удалось загрузить экскурсии. Обновите страницу.</p>
          : !data?.results.length ? <p className='py-8'>Экскурсии не найдены. Попробуйте изменить фильтры.</p>
          : <><div className={`grid grid-cols-1 sm:grid-cols-2 ${desktopVisible ? 'xl:grid-cols-3' : 'xl:grid-cols-4'} gap-6 mb-8`}>{data.results.map(excursion => <ExcursionCard key={excursion.id} excursion={excursion} source='catalog' />)}</div>
            {totalPages > 1 && <nav aria-label='Страницы каталога' className='flex flex-wrap justify-center gap-2'>
              {page > 1 && <button onClick={() => goToPage(page - 1)} className='border rounded px-3 py-2'>Предыдущая</button>}
              {paginationItems.map((item, index) => item === 'ellipsis'
                ? <span key={`ellipsis-${index}`} aria-hidden='true' className='px-2 py-2 text-gray-500'>…</span>
                : <button key={item} aria-label={`Страница ${item}`} aria-current={page === item ? 'page' : undefined} onClick={() => goToPage(item)} className={`border rounded px-3 py-2 ${page === item ? 'bg-primary text-white' : ''}`}>{item}</button>)}
              {page < totalPages && <button onClick={() => goToPage(page + 1)} className='border rounded px-3 py-2'>Следующая</button>}
            </nav>}
          </>}
      </div>
    </div>
  </main>
}
