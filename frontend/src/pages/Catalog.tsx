import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import FilterSidebar, {
  type FilterState,
} from '../components/catalog/FilterSidebar'
import ExcursionCard from '../components/ExcursionCard'
import { excursionsApi } from '../api/excursions'
import type { Excursion } from '../types'

export default function Catalog() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [filters, setFilters] = useState<FilterState>({
    category: searchParams.get('category') || '',
    minPrice: Number(searchParams.get('min_price')) || 0,
    maxPrice: Number(searchParams.get('max_price')) || 10000,
    location: searchParams.get('location') || '',
    duration: searchParams.get('duration') || '',
    date: searchParams.get('date') || '',
  })
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1)
  const [sortBy, setSortBy] = useState(searchParams.get('sort') || 'popular')

  useEffect(() => {
    const params: Record<string, string> = {}
    if (filters.category) params.category = filters.category
    if (filters.minPrice) params.min_price = filters.minPrice.toString()
    if (filters.maxPrice) params.max_price = filters.maxPrice.toString()
    if (filters.location) params.location = filters.location
    if (filters.duration) params.duration = filters.duration
    if (filters.date) params.date = filters.date
    if (page > 1) params.page = page.toString()
    if (sortBy !== 'popular') params.sort = sortBy
    setSearchParams(params)
  }, [filters, page, sortBy, setSearchParams])

  const {
    data: excursionsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['excursions', filters, page, sortBy],
    queryFn: () =>
      excursionsApi.getExcursions({
        page,
        category: filters.category || undefined,
        min_price: filters.minPrice || undefined,
        max_price: filters.maxPrice || undefined,
        location_type: filters.location || undefined,
        search: searchParams.get('search') || undefined,
      }),
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
    setSortBy(value)
    setPage(1)
  }

  return (
    <div className='max-w-6xl mx-auto px-4 py-8'>
      <div className='flex flex-col lg:flex-row gap-8'>
        <FilterSidebar onFiltersChange={handleFiltersChange} />

        <div className='flex-1'>
          <div className='flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4'>
            <h1 className='text-2xl font-bold'>
              {filters.category ? filters.category : 'Все экскурсии'}
            </h1>
            <p className='text-gray-600'>Найдено {totalCount} экскурсий</p>
          </div>

          <div className='flex items-center gap-4 mb-6'>
            <label className='text-sm text-gray-700'>Сортировка:</label>
            <select
              value={sortBy}
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
