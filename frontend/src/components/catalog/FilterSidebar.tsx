import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { excursionsApi } from '../../api/excursions';
import type { Category } from '../../types';

interface FilterSidebarProps {
  onFiltersChange: (filters: FilterState) => void;
  filters: FilterState;
}

export interface FilterState {
  categories: string[];
  minPrice: number;
  maxPrice: number;
  location: string;
  duration: string;
  dateFrom: string;
  dateTo: string;
}

const locations = [
  { value: 'city', label: 'Городские экскурсии' },
  { value: 'suburban', label: 'Загородные экскурсии' },
  { value: 'russia', label: 'Туры по России' },
];
const durations = ['до 2ч', '2-4ч', 'более 4ч'];

export default function FilterSidebar({ onFiltersChange, filters }: FilterSidebarProps) {
  const [localFilters, setLocalFilters] = useState<FilterState>(filters)

  // Синхронизируем локальное состояние с props
  useEffect(() => {
    setLocalFilters(filters)
  }, [filters])

  const { data: categories = [], isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => excursionsApi.getCategories(),
    staleTime: 10 * 60 * 1000, // 10 минут
  });

  const handleFilterChange = (key: keyof FilterState, value: string | number | string[]) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleCategoryToggle = (categorySlug: string) => {
    const newCategories = localFilters.categories.includes(categorySlug)
      ? localFilters.categories.filter(c => c !== categorySlug)
      : [...localFilters.categories, categorySlug];
    handleFilterChange('categories', newCategories);
  };

  return (
    <aside className="w-full md:w-64 flex-shrink-0">
      <div className="bg-white rounded-xl shadow-sm p-6 sticky top-20">
        <h3 className="text-lg font-semibold mb-6">Фильтры</h3>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Категории</label>
            <div className="space-y-2">
              {categoriesLoading ? (
                <span className="text-sm text-gray-500">Загрузка...</span>
              ) : categories.length > 0 ? (
                categories.map((cat: Category) => (
                  <label key={cat.slug} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={localFilters.categories.includes(cat.slug)}
                      onChange={() => handleCategoryToggle(cat.slug)}
                      className="w-4 h-4 text-primary rounded border-gray-300 focus:ring-primary"
                    />
                    <span className="text-sm text-gray-700">{cat.name}</span>
                  </label>
                ))
              ) : (
                <span className="text-sm text-gray-500">Нет категорий</span>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Цена (₽)</label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={localFilters.minPrice}
                onChange={(e) => handleFilterChange('minPrice', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="От"
              />
              <span className="text-gray-500">—</span>
              <input
                type="number"
                value={localFilters.maxPrice}
                onChange={(e) => handleFilterChange('maxPrice', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="До"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Локация</label>
            <select
              value={localFilters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Все локации</option>
              {locations.map((loc) => (
                <option key={loc.value} value={loc.value}>
                  {loc.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Длительность</label>
            <select
              value={localFilters.duration}
              onChange={(e) => handleFilterChange('duration', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Любая</option>
              {durations.map((dur) => (
                <option key={dur} value={dur}>
                  {dur}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Дата от</label>
            <input
              type="date"
              value={localFilters.dateFrom}
              onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary mb-2"
            />
            <label className="block text-sm font-medium text-gray-700 mb-3">Дата до</label>
            <input
              type="date"
              value={localFilters.dateTo}
              onChange={(e) => handleFilterChange('dateTo', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      </div>
    </aside>
  );
}
