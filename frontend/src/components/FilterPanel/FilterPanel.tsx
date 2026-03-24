import { LandsFilterRequest } from '@/types'
import '../../styles/FilterPanel.css'

interface FilterPanelProps {
  filters: LandsFilterRequest
  onFilterChange: (filters: Partial<LandsFilterRequest>) => void
}

export default function FilterPanel({ filters, onFilterChange }: FilterPanelProps) {
  const handleInputChange = (
    field: keyof LandsFilterRequest,
    value: any
  ) => {
    onFilterChange({
      [field]: value === '' ? undefined : value,
    })
  }

  return (
    <div className="filter-panel">
      <h3>Фильтры</h3>

      <div className="filter-group">
        <label>Поиск</label>
        <input
          type="text"
          placeholder="Название, адрес, кадастровый номер..."
          value={filters.search_query || ''}
          onChange={(e) => handleInputChange('search_query', e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label>Регион / Республика</label>
        <input
          type="text"
          placeholder="Например: Московская область"
          value={filters.region_name || ''}
          onChange={(e) => handleInputChange('region_name', e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label>Населённый пункт</label>
        <input
          type="text"
          placeholder="Например: Химки"
          value={filters.city_name || ''}
          onChange={(e) => handleInputChange('city_name', e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label>Тип сделки</label>
        <select
          value={filters.deal_type || ''}
          onChange={(e) => handleInputChange('deal_type', e.target.value)}
        >
          <option value="">Любой</option>
          <option value="purchase">Покупка</option>
          <option value="lease">Аренда</option>
          <option value="rent">Сдача в наём</option>
          <option value="auction">Аукцион</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Тип объявления</label>
        <select
          value={filters.listing_type || ''}
          onChange={(e) => handleInputChange('listing_type', e.target.value)}
        >
          <option value="">Все</option>
          <option value="owner">От собственника</option>
          <option value="agency">От агентства</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Участок</label>
        <select
          value={filters.has_building === undefined ? '' : filters.has_building ? 'with' : 'without'}
          onChange={(e) => {
            const val = e.target.value
            handleInputChange('has_building', val === '' ? undefined : val === 'with')
          }}
        >
          <option value="">Все участки</option>
          <option value="without">Пустые участки</option>
          <option value="with">С домом</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Категория земли</label>
        <select
          value={filters.land_category || ''}
          onChange={(e) => handleInputChange('land_category', e.target.value)}
        >
          <option value="">Любая</option>
          <option value="residential">Жилая</option>
          <option value="commercial">Коммерческая</option>
          <option value="agricultural">Сельскохозяйственная</option>
          <option value="industrial">Промышленная</option>
        </select>
      </div>

      <div className="filter-row">
        <div className="filter-group">
          <label>Цена от (₽)</label>
          <input
            type="number"
            placeholder="Мин"
            value={filters.price_min ?? ''}
            onChange={(e) => handleInputChange('price_min', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>
        <div className="filter-group">
          <label>Цена до (₽)</label>
          <input
            type="number"
            placeholder="Макс"
            value={filters.price_max ?? ''}
            onChange={(e) => handleInputChange('price_max', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>
      </div>

      <div className="filter-row">
        <div className="filter-group">
          <label>Площадь от (м²)</label>
          <input
            type="number"
            placeholder="Мин"
            value={filters.area_min ?? ''}
            onChange={(e) => handleInputChange('area_min', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>
        <div className="filter-group">
          <label>Площадь до (м²)</label>
          <input
            type="number"
            placeholder="Макс"
            value={filters.area_max ?? ''}
            onChange={(e) => handleInputChange('area_max', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>
      </div>

      <button
        className="clear-filters-btn"
        onClick={() => {
          onFilterChange({
            search_query: undefined,
            deal_type: undefined,
            listing_type: undefined,
            has_building: undefined,
            land_category: undefined,
            price_min: undefined,
            price_max: undefined,
            area_min: undefined,
            area_max: undefined,
            region_name: undefined,
            city_name: undefined,
          })
        }}
      >
        Очистить фильтры
      </button>
    </div>
  )
}
