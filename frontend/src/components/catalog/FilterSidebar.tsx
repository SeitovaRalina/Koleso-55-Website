import { useState } from 'react';

interface FilterSidebarProps {
  onFiltersChange: (filters: FilterState) => void;
}

export interface FilterState {
  category: string;
  minPrice: number;
  maxPrice: number;
  location: string;
  duration: string;
  date: string;
}

const categories = ['Обзорные', 'Активные', 'Мастер-классы', 'Дегустации', 'Авторские'];
const locations = ['Омск', 'Омская область', 'Россия'];
const durations = ['до 2ч', '2-4ч', 'более 4ч'];

export default function FilterSidebar({ onFiltersChange }: FilterSidebarProps) {
  const [filters, setFilters] = useState<FilterState>({
    category: '',
    minPrice: 0,
    maxPrice: 10000,
    location: '',
    duration: '',
    date: '',
  });

  const handleFilterChange = (key: keyof FilterState, value: string | number) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  return (
    <aside className="w-full md:w-64 flex-shrink-0">
      <div className="bg-white rounded-xl shadow-sm p-6 sticky top-20">
        <h3 className="text-lg font-semibold mb-6">Фильтры</h3>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Категория</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleFilterChange('category', '')}
                className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                  !filters.category
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Все
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => handleFilterChange('category', cat)}
                  className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                    filters.category === cat
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Цена (₽)</label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={filters.minPrice}
                onChange={(e) => handleFilterChange('minPrice', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="От"
              />
              <span className="text-gray-500">—</span>
              <input
                type="number"
                value={filters.maxPrice}
                onChange={(e) => handleFilterChange('maxPrice', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="До"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Локация</label>
            <select
              value={filters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Все локации</option>
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Длительность</label>
            <select
              value={filters.duration}
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
            <label className="block text-sm font-medium text-gray-700 mb-3">Дата</label>
            <input
              type="date"
              value={filters.date}
              onChange={(e) => handleFilterChange('date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      </div>
    </aside>
  );
}
