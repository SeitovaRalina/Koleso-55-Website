import { useState, useEffect, type FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import FilterSidebar, {
  type FilterState,
} from '../components/catalog/FilterSidebar'
import ExcursionCard from '../components/ExcursionCard'
import { excursionsApi } from '../api/excursions'
import type { Excursion, Category } from '../types'

export default function Catalog() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '')

  // Загружаем максимальную цену
  const { data: maxPrice = 10000 } = useQuery({
    queryKey: ['maxPrice'],
    queryFn: () => excursionsApi.getMaxPrice(),
    staleTime: 60 * 60 * 1000, // 1 час
  })

  const [filters, setFilters] = useState<FilterState>({
    categories: searchParams.getAll('category') || [],
    minPrice: Number(searchParams.get('min_price')) || 0,
    maxPrice: Number(searchParams.get('max_price')) || maxPrice,
    location: searchParams.get('location_type') || '',
    duration: searchParams.get('duration') || '',
    dateFrom: searchParams.get('date_from') || '',
    dateTo: searchParams.get('date_to') || '',
  })

  // Обновляем maxPrice после загрузки
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1)
  const [sortUiValue, setSortUiValue] = useState('popular')

  // Загружаем категории для отображения названия
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: () => excursionsApi.getCategories(),
    staleTime: 10 * 60 * 1000,
  })

  const getCategoryName = (slug: string) => {
    const category = categories.find((cat: Category) => cat.slug === slug)
    return category?.name || slug
  }

  const getCategoryNames = (slugs: string[]) => {
    return slugs.map(slug => getCategoryName(slug)).join(', ')
  }

  useEffect(() => {
    const params = new URLSearchParams()
    // Сохраняем search параметр
    const currentSearch = searchParams.get('search')
    if (currentSearch) params.set('search', currentSearch)

    filters.categories.forEach(cat => {
      params.append('category', cat)
    })
    if (filters.minPrice > 0) params.set('min_price', filters.minPrice.toString())
    if (filters.maxPrice > 0) params.set('max_price', filters.maxPrice.toString())
    if (filters.location) params.set('location_type', filters.location)
    if (filters.duration) params.set('duration', filters.duration)
    if (filters.dateFrom) params.set('date_from', filters.dateFrom)
    if (filters.dateTo) params.set('date_to', filters.dateTo)
    if (page > 1) params.set('page', page.toString())
    if (sortUiValue !== 'popular') {
      // Конвертируем UI значение в ordering
      let ordering: string
      if (sortUiValue === 'price_asc') ordering = 'price'
      else if (sortUiValue === 'price_desc') ordering = '-price'
      else if (sortUiValue === 'duration') ordering = 'duration'
      else if (sortUiValue === 'newest') ordering = '-created_at'
      else ordering = '-created_at'
      params.set('ordering', ordering)
    }
    setSearchParams(params)
  }, [filters, page, sortUiValue, setSearchParams, searchParams])

  const {
    data: excursionsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['excursions', filters, page, sortUiValue, searchParams.get('search')],
    queryFn: () => {
      // Конвертируем duration в min_duration/max_duration
      let minDuration: number | undefined
      let maxDuration: number | undefined
      if (filters.duration === 'до 2ч') {
        maxDuration = 120
      } else if (filters.duration === '2-4ч') {
        minDuration = 120
        maxDuration = 240
      } else if (filters.duration === 'более 4ч') {
        minDuration = 240
      }

      // Конвертируем UI значение в ordering для API
      let ordering: string | undefined
      if (sortUiValue === 'price_asc') ordering = 'price'
      else if (sortUiValue === 'price_desc') ordering = '-price'
      else if (sortUiValue === 'duration') ordering = 'duration'
      else if (sortUiValue === 'newest') ordering = '-created_at'
      else if (sortUiValue === 'popular') ordering = '-created_at'

      const params = {
        page,
        category: filters.categories.length > 0 ? filters.categories : undefined,
        min_price: filters.minPrice > 0 ? filters.minPrice : undefined,
        max_price: filters.maxPrice > 0 ? filters.maxPrice : undefined,
        location_type: filters.location || undefined,
        min_duration: minDuration,
        max_duration: maxDuration,
        date_from: filters.dateFrom || undefined,
        date_to: filters.dateTo || undefined,
        search: searchParams.get('search') || undefined,
        ordering,
      }

      return excursionsApi.getExcursions(params)
    },
    staleTime: 5 * 60 * 1000,
  })

  const excursions = excursionsData?.results || []
  const totalCount = excursionsData?.count || 0
  const totalPages = Math.ceil(totalCount / 12)

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters)
    setPage(1)
  }

  const handleSortChange = (value: string) => {
    setSortUiValue(value)
    setPage(1)
  }

  const handleSearch = (e: FormEvent) => {
    e.preventDefault()
    const params = new URLSearchParams(searchParams)
    if (searchQuery.trim()) {
      params.set('search', searchQuery.trim())
    } else {
      params.delete('search')
    }
    params.delete('page')
    setSearchParams(params)
    setPage(1)
  }

  const clearSearch = () => {
    setSearchQuery('')
    const params = new URLSearchParams(searchParams)
    params.delete('search')
    params.delete('page')
    setSearchParams(params)
    setPage(1)
  }

  return (
    <div className='max-w-6xl mx-auto px-4 py-8'>
      <div className='flex flex-col lg:flex-row gap-8'>
        <FilterSidebar onFiltersChange={handleFiltersChange} filters={filters} />

        <div className='flex-1'>
          <div className='flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4'>
            <div>
              <h1 className='text-2xl font-bold'>
                {searchParams.get('search')
                  ? `Результаты поиска: "${searchParams.get('search')}"`
                  : filters.categories.length > 0
                  ? getCategoryNames(filters.categories)
                  : 'Все экскурсии'}
              </h1>
              <p className='text-gray-600 mt-1'>Найдено {totalCount} экскурсий</p>
            </div>
          </div>

          <form onSubmit={handleSearch} className='mb-6'>
            <div className='flex gap-2'>
              <input
                type='text'
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder='Поиск по названию и описанию...'
                className='flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
              />
              <button
                type='submit'
                className='px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors'
              >
                Найти
              </button>
              {searchParams.get('search') && (
                <button
                  type='button'
                  onClick={clearSearch}
                  className='px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors'
                >
                  Сбросить
                </button>
              )}
            </div>
          </form>

          <div className='flex items-center gap-4 mb-6'>
            <label className='text-sm text-gray-700'>Сортировка:</label>
            <select
              value={sortUiValue}
              onChange={e => handleSortChange(e.target.value)}
              className='px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
            >
              <option value='popular'>По популярности</option>
              <option value='price_asc'>Цена: по возрастанию</option>
              <option value='price_desc'>Цена: по убыванию</option>
              <option value='duration'>По длительности</option>
              <option value='newest'>Сначала новые</option>
            </select>
          </div>

          {isLoading ? (
            <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6'>
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className='bg-gray-200 rounded-xl h-96 animate-pulse'
                />
              ))}
            </div>
          ) : error ? (
            <div className='text-center py-12'>
              <p className='text-gray-600'>Ошибка загрузки экскурсий</p>
            </div>
          ) : excursions.length === 0 ? (
            <div className='text-center py-12'>
              <p className='text-gray-600'>Экскурсии не найдены</p>
            </div>
          ) : (
            <>
              <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8'>
                {excursions.map((excursion: Excursion) => (
                  <ExcursionCard key={excursion.id} excursion={excursion} source='catalog' />
                ))}
              </div>

              {totalPages > 1 && (
                <div className='flex items-center justify-center gap-2'>
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className='px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
                  >
                    Назад
                  </button>
                  {[...Array(totalPages)].map((_, i) => {
                    const pageNum = i + 1
                    const showPage =
                      pageNum === 1 ||
                      pageNum === totalPages ||
                      (pageNum >= page - 1 && pageNum <= page + 1)

                    if (!showPage) {
                      if (pageNum === page - 2 || pageNum === page + 2) {
                        return (
                          <span key={pageNum} className='px-2'>
                            ...
                          </span>
                        )
                      }
                      return null
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`px-4 py-2 border rounded-lg ${page === pageNum
                            ? 'bg-primary text-white border-primary'
                            : 'border-gray-300 hover:bg-gray-50'
                          }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className='px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
                  >
                    Вперед
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
