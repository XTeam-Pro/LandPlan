import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Category, Service } from '@/types'
import { servicesApi } from '@/api/services'
import '../styles/ServicesPage.css'

export default function ServicesPage() {
  const navigate = useNavigate()
  const [categories, setCategories] = useState<Category[]>([])
  const [services, setServices] = useState<Service[]>([])
  const [expandedCategory, setExpandedCategory] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [cats, svcs] = await Promise.all([
          servicesApi.getCategories(),
          servicesApi.list(),
        ])
        setCategories(cats)
        setServices(svcs)
      } catch (err) {
        console.error('Failed to load services', err)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [])

  const getServicesByCategory = (categoryId: number) =>
    services.filter((s) => s.category_id === categoryId && s.is_active)

  const priorityLabel = (p: string) => {
    if (p === 'critical') return 'Обязательная'
    if (p === 'recommended') return 'Рекомендуемая'
    return 'Опциональная'
  }

  return (
    <div className="services-page">
      <header className="page-header">
        <div className="header-content">
          <h1>Каталог услуг</h1>
          <p>Все виды работ для освоения земельного участка</p>
        </div>
        <nav className="header-nav">
          <button onClick={() => navigate('/')} className="btn-secondary">На карту</button>
          <button onClick={() => navigate('/companies')} className="btn-secondary">Компании</button>
        </nav>
      </header>

      {isLoading ? (
        <div className="loading-spinner">Загрузка каталога...</div>
      ) : (
        <div className="categories-list">
          {categories.filter(c => c.is_active).sort((a, b) => a.sort_order - b.sort_order).map((cat) => {
            const catServices = getServicesByCategory(cat.id)
            const isExpanded = expandedCategory === cat.id

            return (
              <div key={cat.id} className={`category-card ${isExpanded ? 'expanded' : ''}`}>
                <div
                  className="category-header"
                  onClick={() => setExpandedCategory(isExpanded ? null : cat.id)}
                >
                  <span className="category-icon">{cat.icon || '🔧'}</span>
                  <h3>{cat.name}</h3>
                  <span className="service-count">{catServices.length} услуг</span>
                  <span className="expand-icon">{isExpanded ? '▲' : '▼'}</span>
                </div>

                {isExpanded && (
                  <div className="services-list">
                    {catServices.length > 0 ? catServices.map((svc) => (
                      <div key={svc.id} className="service-item">
                        <div className="service-info">
                          <h4>{svc.name}</h4>
                          {svc.short_description && (
                            <p className="service-desc">{svc.short_description}</p>
                          )}
                        </div>
                        <div className="service-meta">
                          <span className={`priority-badge priority-${svc.priority}`}>
                            {priorityLabel(svc.priority)}
                          </span>
                          <button
                            className="btn-small"
                            onClick={() => navigate(`/companies?service_id=${svc.id}`)}
                          >
                            Найти подрядчиков
                          </button>
                        </div>
                      </div>
                    )) : (
                      <p className="no-services">Нет доступных услуг в этой категории</p>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
