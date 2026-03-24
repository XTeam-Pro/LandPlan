import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLandsStore } from '@/store/landsStore'
import { useAuthStore } from '@/store/authStore'
import { Category } from '@/types'
import { servicesApi } from '@/api/services'
import MapView from '@/components/Map/MapView'
import FilterPanel from '@/components/FilterPanel/FilterPanel'
import LandCard from '@/components/LandCard/LandCard'
import '../styles/MapPage.css'

const SERVICE_ICONS: Record<string, string> = {
  'Водоснабжение': '💧',
  'Электроснабжение': '⚡',
  'Газификация': '🔥',
  'Кадастровые работы': '📐',
  'Геология и геодезия': '🔬',
  'Юридические услуги': '⚖️',
  'Строительство': '🏗️',
  'Проектирование': '📋',
  'Ландшафтный дизайн': '🌳',
  'Дренаж и мелиорация': '🌊',
  'Дорожные работы': '🛣️',
  'Оценка': '📊',
  'Агентства недвижимости': '🏠',
  'Охрана и безопасность': '🔒',
}

export default function MapPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { lands, total, filters, selectedLand, isLoading, setFilters, fetchLands, selectLand } =
    useLandsStore()
  const [categories, setCategories] = useState<Category[]>([])

  useEffect(() => {
    fetchLands()
    servicesApi.getCategories().then(setCategories).catch(() => {})
  }, [])

  const handleLandSelect = (id: number) => {
    selectLand(id)
    navigate(`/land/${id}`)
  }

  return (
    <div className="map-page">
      {/* Header */}
      <header className="page-header">
        <div className="header-content">
          <h1 className="logo-title" onClick={() => navigate('/')}>Моя Земля</h1>
        </div>
        <nav className="header-nav">
          <button onClick={() => navigate('/bankruptcy-auctions')} className="btn-secondary">
            Торги по банкротству
          </button>
          <button onClick={() => navigate('/government-sales')} className="btn-secondary">
            Государственные торги
          </button>
          {user ? (
            <>
              <button onClick={() => navigate('/create-listing')} className="btn-primary-nav">
                + Разместить объявление
              </button>
              <span className="user-name">{user.full_name}</span>
              <button onClick={() => navigate('/cabinet')} className="btn-secondary">
                Мой кабинет
              </button>
            </>
          ) : (
            <button onClick={() => navigate('/auth')} className="btn-secondary">
              Вход
            </button>
          )}
        </nav>
      </header>

      {/* Services icons bar */}
      <div className="services-icon-bar">
        {categories
          .filter((c) => c.is_active)
          .sort((a, b) => a.sort_order - b.sort_order)
          .map((cat) => (
            <button
              key={cat.id}
              className="service-icon-btn"
              onClick={() => navigate(`/services?category=${cat.id}`)}
              title={cat.name}
            >
              <span className="service-icon-emoji">{SERVICE_ICONS[cat.name] || cat.icon || '🔧'}</span>
              <span className="service-icon-label">{cat.name}</span>
            </button>
          ))}
      </div>

      {/* Main content */}
      <div className="map-page-content">
        {/* Left sidebar - Filters */}
        <aside className="sidebar sidebar-left">
          <FilterPanel filters={filters} onFilterChange={setFilters} />
        </aside>

        {/* Center - Map */}
        <main className="map-container-main">
          {isLoading && <div className="loading-spinner">Загрузка карты...</div>}
          <MapView
            lands={lands}
            selectedLandId={selectedLand?.id}
            onLandSelect={handleLandSelect}
          />
        </main>

        {/* Right sidebar - Land list */}
        <aside className="sidebar sidebar-right">
          <div className="lands-list-header">
            <h3>Найдено участков: {total}</h3>
            {isLoading && <span className="loading-text">Загрузка...</span>}
          </div>

          <div className="lands-list">
            {lands.length > 0 ? (
              lands.map((land) => (
                <LandCard
                  key={land.id}
                  land={land}
                  isSelected={selectedLand?.id === land.id}
                  onClick={handleLandSelect}
                />
              ))
            ) : (
              <p className="no-results">Участки не найдены. Попробуйте изменить фильтры.</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
