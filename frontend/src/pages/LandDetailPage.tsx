import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useLandsStore } from '@/store/landsStore'
import { useAuthStore } from '@/store/authStore'
import { LandCompaniesResponse } from '@/types'
import { landsApi } from '@/api/lands'
import RecommendationsBlock from '@/components/RecommendationsBlock/RecommendationsBlock'
import ApplicationModal from '@/components/ApplicationModal/ApplicationModal'
import CreatePlanModal from '@/components/CreatePlanModal/CreatePlanModal'
import '../styles/LandDetailPage.css'

const SUPPORT_PHONE = '8-800-000-00-00'

const dealTypeRu: Record<string, string> = {
  purchase: 'Покупка', lease: 'Аренда', rent: 'Сдача в наём', auction: 'Аукцион',
}
const categoryRu: Record<string, string> = {
  residential: 'Жилая', commercial: 'Коммерческая',
  agricultural: 'Сельскохозяйственная', industrial: 'Промышленная',
  'жилая': 'Жилая', 'коммерческая': 'Коммерческая',
  'сельскохозяйственная': 'Сельскохозяйственная', 'промышленная': 'Промышленная',
}
const priorityRu: Record<string, string> = {
  critical: 'Обязательно', recommended: 'Рекомендуется', optional: 'Опционально',
}
const listingTypeLabel: Record<string, string> = {
  owner: 'от собственника',
  agency: 'от агентства',
}

export default function LandDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { selectedLand, recommendations, isLoading, selectLand } = useLandsStore()

  const [landCompanies, setLandCompanies] = useState<LandCompaniesResponse | null>(null)
  const [showCreatePlan, setShowCreatePlan] = useState(false)
  const [applicationTarget, setApplicationTarget] = useState<{
    serviceId: number; serviceName: string; companyId: number; companyName: string
  } | null>(null)

  useEffect(() => {
    if (id) {
      selectLand(parseInt(id))
      landsApi.getCompanies(parseInt(id)).then(setLandCompanies).catch(() => {})
    }
  }, [id])

  const handleCreateApplication = (serviceId: number, serviceName: string, companyId: number, companyName: string) => {
    if (!user) {
      navigate('/auth')
      return
    }
    setApplicationTarget({ serviceId, serviceName, companyId, companyName })
  }

  if (isLoading) {
    return (
      <div className="land-detail-page">
        <div className="loading-spinner">Загрузка информации об участке...</div>
      </div>
    )
  }

  if (!selectedLand) {
    return (
      <div className="land-detail-page">
        <div className="error-message">Участок не найден</div>
        <button onClick={() => navigate('/')} className="btn-primary">Вернуться на карту</button>
      </div>
    )
  }

  return (
    <div className="land-detail-page">
      <header className="detail-header">
        <button onClick={() => navigate('/')} className="btn-back">← Вернуться на карту</button>
        <nav className="header-nav">
          {user ? (
            <>
              <span className="user-name">{user.full_name}</span>
              <button onClick={() => navigate('/cabinet')} className="btn-secondary">Мой кабинет</button>
            </>
          ) : (
            <button onClick={() => navigate('/auth')} className="btn-secondary">Войти для подачи заявки</button>
          )}
        </nav>
      </header>

      <div className="detail-content">
        <main className="main-column">
          <div className="land-detail">
            {/* Listing type badge */}
            <div className="detail-badges">
              {selectedLand.listing_type && listingTypeLabel[selectedLand.listing_type] && (
                <span className={`listing-badge-lg listing-${selectedLand.listing_type}`}>
                  {listingTypeLabel[selectedLand.listing_type]}
                </span>
              )}
              {selectedLand.has_building && (
                <span className="building-badge-lg">С домом</span>
              )}
            </div>

            {/* Cadastral number — FIRST LINE */}
            {selectedLand.cadastral_number && (
              <div className="cadastral-number-block">
                <span className="cadastral-label">Кадастровый номер:</span>
                <span className="cadastral-value">{selectedLand.cadastral_number}</span>
                <a
                  href={`https://nspd.gov.ru/map?thematicMapId=1&cadastralNumber=${selectedLand.cadastral_number}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="nspd-link"
                >
                  Посмотреть на НСПД
                </a>
              </div>
            )}

            <h1>{selectedLand.title}</h1>

            {/* Photo gallery */}
            <div className="photo-gallery">
              {selectedLand.photos && selectedLand.photos.length > 0 ? (
                <div className="photo-grid">
                  {selectedLand.photos.map((photo, idx) => (
                    <div key={idx} className="photo-item">
                      <img src={photo} alt={`Фото ${idx + 1}`} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="photo-placeholder">
                  <span>{selectedLand.has_building ? '🏠' : '🌿'}</span>
                  <p>Фото не добавлены</p>
                </div>
              )}
            </div>

            {/* Contact buttons */}
            <div className="contact-buttons">
              <a
                href={`tel:${selectedLand.contact_phone || SUPPORT_PHONE}`}
                className="btn-contact btn-call"
              >
                Позвонить
              </a>
              <a
                href={`mailto:?subject=Запрос по участку ${selectedLand.cadastral_number || selectedLand.title}`}
                className="btn-contact btn-write"
              >
                Написать
              </a>
            </div>

            <div className="land-info">
              <h2>Информация об участке</h2>
              <div className="info-grid">
                <div className="info-item">
                  <span className="label">Адрес</span>
                  <span className="value">{selectedLand.address}</span>
                </div>
                {selectedLand.price != null && (
                  <div className="info-item">
                    <span className="label">Цена</span>
                    <span className="value">{selectedLand.price.toLocaleString()} ₽</span>
                  </div>
                )}
                {selectedLand.area != null && (
                  <div className="info-item">
                    <span className="label">Площадь</span>
                    <span className="value">{selectedLand.area.toLocaleString()} м²</span>
                  </div>
                )}
                {selectedLand.deal_type && (
                  <div className="info-item">
                    <span className="label">Тип сделки</span>
                    <span className="value">{dealTypeRu[selectedLand.deal_type] || selectedLand.deal_type}</span>
                  </div>
                )}
                {selectedLand.land_category && (
                  <div className="info-item">
                    <span className="label">Категория</span>
                    <span className="value">{categoryRu[selectedLand.land_category!] || selectedLand.land_category}</span>
                  </div>
                )}
                {selectedLand.allowed_usage && (
                  <div className="info-item">
                    <span className="label">Вид разрешённого использования</span>
                    <span className="value">{selectedLand.allowed_usage}</span>
                  </div>
                )}
              </div>
              {selectedLand.description && (
                <div className="description">
                  <h3>Описание</h3>
                  <p>{selectedLand.description}</p>
                </div>
              )}
            </div>

            {selectedLand.features && (
              <div className="features-section">
                <h3>Характеристики участка</h3>
                <div className="features-grid">
                  {[
                    { key: 'has_water', icon: '💧', label: 'Вода', yes: 'Доступна', no: 'Отсутствует' },
                    { key: 'has_electricity', icon: '⚡', label: 'Электричество', yes: 'Доступно', no: 'Отсутствует' },
                    { key: 'has_gas', icon: '🔥', label: 'Газ', yes: 'Доступен', no: 'Отсутствует' },
                    { key: 'has_roads', icon: '🛣️', label: 'Дороги', yes: 'Доступны', no: 'Отсутствуют' },
                    { key: 'boundaries_defined', icon: '🗺️', label: 'Границы', yes: 'Определены', no: 'Не определены' },
                    { key: 'build_ready', icon: '🏗️', label: 'Готов к строительству', yes: 'Да', no: 'Нет' },
                  ].map(({ key, icon, label, yes, no }) => {
                    const val = (selectedLand.features as any)[key]
                    return (
                      <div key={key} className={`feature-item ${val ? 'available' : 'unavailable'}`}>
                        <span className="feature-icon">{icon}</span>
                        <span className="feature-label">{label}</span>
                        <span className="feature-status">{val ? yes : no}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Companies by service */}
            {landCompanies && landCompanies.services_with_companies.length > 0 && (
              <div className="land-companies-section">
                <h2>Подрядчики для вашего участка</h2>
                {landCompanies.services_with_companies.map((svc) => (
                  <div key={svc.service_id} className="service-companies-group">
                    <div className="service-group-header">
                      <h4>{svc.service_name}</h4>
                      <span className={`priority-badge priority-${svc.priority}`}>{priorityRu[svc.priority] || svc.priority}</span>
                    </div>
                    {svc.companies.length > 0 ? (
                      <div className="companies-row">
                        {svc.companies.map((company) => (
                          <div key={company.id} className="mini-company-card">
                            <div className="mini-company-info">
                              <span className="company-name" onClick={() => navigate(`/company/${company.id}`)}>
                                {company.public_name}
                              </span>
                              <span className="company-rating">
                                {'★'.repeat(Math.round(company.rating))} {company.rating.toFixed(1)}
                              </span>
                            </div>
                            <button
                              className="btn-small btn-primary"
                              onClick={() => handleCreateApplication(
                                svc.service_id, svc.service_name,
                                company.id, company.public_name
                              )}
                            >
                              Подать заявку
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="no-companies">Нет подрядчиков в вашем регионе</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>

        {recommendations && (
          <aside className="sidebar sidebar-right">
            <RecommendationsBlock
              recommendations={recommendations}
              onCreatePlan={() => {
                if (!user) {
                  navigate('/auth')
                } else {
                  setShowCreatePlan(true)
                }
              }}
            />
          </aside>
        )}
      </div>

      {/* Modals */}
      {applicationTarget && selectedLand && (
        <ApplicationModal
          landId={selectedLand.id}
          serviceId={applicationTarget.serviceId}
          serviceName={applicationTarget.serviceName}
          companyId={applicationTarget.companyId}
          companyName={applicationTarget.companyName}
          onClose={() => setApplicationTarget(null)}
          onSuccess={() => {
            setApplicationTarget(null)
            alert('Заявка успешно отправлена!')
          }}
        />
      )}

      {showCreatePlan && recommendations && selectedLand && (
        <CreatePlanModal
          landId={selectedLand.id}
          recommendations={recommendations}
          onClose={() => setShowCreatePlan(false)}
        />
      )}
    </div>
  )
}
