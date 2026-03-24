import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { LandPlanDetail, ApplicationDetail, ApplicationStats, CompanyDetail } from '@/types'
import { landPlansApi } from '@/api/landPlans'
import { applicationsApi } from '@/api/applications'
import { companiesApi } from '@/api/companies'
import { companyDashboardApi } from '@/api/companyDashboard'
import ApplicationsList from '@/components/Applications/ApplicationsList'
import '../styles/CabinetPage.css'

// ============================================================
// Кабинет пользователя
// ============================================================
function UserCabinet() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [plans, setPlans] = useState<LandPlanDetail[]>([])
  const [plansLoading, setPlansLoading] = useState(true)

  useEffect(() => {
    landPlansApi.getMyPlans()
      .then(setPlans)
      .catch(() => {})
      .finally(() => setPlansLoading(false))
  }, [])

  const statusLabel = (s: string) => {
    const m: Record<string, string> = {
      active: 'Активен', paused: 'Приостановлен', completed: 'Завершён',
      pending: 'Ожидает', in_progress: 'В работе',
    }
    return m[s] || s
  }

  return (
    <>
      {/* Профиль */}
      {user && (
        <section className="cabinet-section">
          <h2>Мой профиль</h2>
          <div className="profile-grid">
            <div className="profile-card">
              <div className="avatar-placeholder">{user.full_name.charAt(0).toUpperCase()}</div>
              <div className="profile-details">
                <h3>{user.full_name}</h3>
                <p className="profile-email">{user.email}</p>
                {user.phone && <p className="profile-phone">{user.phone}</p>}
                <span className="role-badge role-user">Пользователь</span>
                <p className="member-since">На платформе с {new Date(user.created_at).toLocaleDateString('ru-RU')}</p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Планы развития */}
      <section className="cabinet-section">
        <div className="section-header">
          <h2>Мои планы развития</h2>
        </div>
        {plansLoading ? (
          <p className="loading-text">Загрузка планов...</p>
        ) : plans.length > 0 ? (
          <div className="plans-grid">
            {plans.map((plan) => {
              const done = plan.steps.filter(s => s.status === 'completed').length
              const total = plan.steps.length
              const pct = total > 0 ? Math.round((done / total) * 100) : 0
              return (
                <div key={plan.id} className="plan-card" onClick={() => navigate(`/plan/${plan.id}`)}>
                  <div className="plan-card-top">
                    <span className={`status-badge status-${plan.status}`}>{statusLabel(plan.status)}</span>
                    <span className="plan-date">{new Date(plan.created_at).toLocaleDateString('ru-RU')}</span>
                  </div>
                  <p className="plan-card-title">{plan.summary || `План для участка #${plan.land_id}`}</p>
                  <div className="mini-progress"><div className="mini-progress-fill" style={{ width: `${pct}%` }} /></div>
                  <span className="progress-label">{done} из {total} этапов выполнено</span>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="empty-state">
            <p>У вас ещё нет планов развития</p>
            <button onClick={() => navigate('/')} className="btn-primary">Найти участок</button>
          </div>
        )}
      </section>

      {/* Заявки */}
      <section className="cabinet-section">
        <ApplicationsList />
      </section>
    </>
  )
}

// ============================================================
// Кабинет компании
// ============================================================
function CompanyCabinet() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [company, setCompany] = useState<CompanyDetail | null>(null)
  const [companyId, setCompanyId] = useState<number | null>(null)
  const [applications, setApplications] = useState<ApplicationDetail[]>([])
  const [stats, setStats] = useState<ApplicationStats | null>(null)
  const [statusFilter, setStatusFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const info = await companyDashboardApi.getMyCompanyInfo()
        if (info.company_id) {
          setCompanyId(info.company_id)
          const [companyData, appsData, statsData] = await Promise.all([
            companiesApi.getById(info.company_id),
            applicationsApi.list(),
            applicationsApi.getStats(),
          ])
          setCompany(companyData)
          setApplications((appsData as any).items || [])
          setStats(statsData)
        }
      } catch (err) {
        console.error('Ошибка загрузки кабинета компании', err)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [])

  const reloadApps = async () => {
    try {
      const appsData = await applicationsApi.list(statusFilter || undefined)
      setApplications((appsData as any).items || [])
    } catch {}
  }

  useEffect(() => { if (companyId) reloadApps() }, [statusFilter])

  const handleStatusChange = async (appId: number, newStatus: string) => {
    try {
      await applicationsApi.updateStatus(appId, { status: newStatus as any })
      reloadApps()
      const statsData = await applicationsApi.getStats()
      setStats(statsData)
    } catch (err: any) {
      alert(err.response?.data?.error || 'Ошибка обновления статуса')
    }
  }

  const statusLabel = (s: string) => {
    const m: Record<string, string> = {
      pending: 'Новая', accepted: 'Принята', in_progress: 'В работе',
      completed: 'Завершена', rejected: 'Отклонена', cancelled: 'Отменена',
    }
    return m[s] || s
  }

  if (isLoading) return <p className="loading-text">Загрузка кабинета компании...</p>

  if (!company) {
    return (
      <section className="cabinet-section">
        <div className="empty-state">
          <h2>Компания не зарегистрирована</h2>
          <p>Вы вошли с ролью «Компания», но профиль компании ещё не создан.</p>
          <button onClick={() => navigate('/companies')} className="btn-primary">Зарегистрировать компанию</button>
        </div>
      </section>
    )
  }

  return (
    <>
      {/* Профиль компании */}
      <section className="cabinet-section">
        <div className="section-header">
          <h2>Профиль компании</h2>
          <button className="btn-secondary btn-sm" onClick={() => navigate(`/company/${company.id}`)}>
            Публичная страница
          </button>
        </div>
        <div className="company-profile-card">
          <div className="company-profile-header">
            <div className="avatar-placeholder company-avatar">{company.public_name.charAt(0)}</div>
            <div>
              <h3>{company.public_name}</h3>
              {company.legal_name !== company.public_name && (
                <p className="legal-name">Юр. лицо: {company.legal_name}</p>
              )}
              <span className={`verification-badge ${company.verification_status}`}>
                {company.verification_status === 'verified' ? 'Проверена' : company.verification_status === 'pending' ? 'На модерации' : 'Не проверена'}
              </span>
            </div>
            <div className="company-rating-block">
              <span className="rating-big">{'★'.repeat(Math.round(company.rating))}</span>
              <span className="rating-number">{company.rating.toFixed(1)}</span>
              <span className="reviews-count">{company.reviews_count} отзывов</span>
            </div>
          </div>
          <div className="company-contacts-row">
            {company.contact_phone && <span>{company.contact_phone}</span>}
            {company.contact_email && <span>{company.contact_email}</span>}
            {company.website && <span>{company.website}</span>}
          </div>
          {company.services && company.services.length > 0 && (
            <div className="company-services-tags">
              <strong>Услуги:</strong>
              {company.services.map(s => (
                <span key={s.id} className="service-tag-sm">{s.service_name}</span>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Статистика заявок */}
      {stats && (
        <section className="cabinet-section">
          <h2>Статистика заявок</h2>
          <div className="stats-grid">
            <div className="stat-card stat-total"><span className="stat-number">{stats.total}</span><span className="stat-label">Всего</span></div>
            <div className="stat-card stat-pending"><span className="stat-number">{stats.pending}</span><span className="stat-label">Новые</span></div>
            <div className="stat-card stat-accepted"><span className="stat-number">{stats.accepted}</span><span className="stat-label">Принятые</span></div>
            <div className="stat-card stat-progress"><span className="stat-number">{stats.in_progress}</span><span className="stat-label">В работе</span></div>
            <div className="stat-card stat-completed"><span className="stat-number">{stats.completed}</span><span className="stat-label">Завершены</span></div>
            <div className="stat-card stat-rejected"><span className="stat-number">{stats.rejected}</span><span className="stat-label">Отклонены</span></div>
          </div>
        </section>
      )}

      {/* Входящие заявки */}
      <section className="cabinet-section">
        <div className="section-header">
          <h2>Входящие заявки</h2>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="status-filter">
            <option value="">Все статусы</option>
            <option value="pending">Новые</option>
            <option value="accepted">Принятые</option>
            <option value="in_progress">В работе</option>
            <option value="completed">Завершённые</option>
            <option value="rejected">Отклонённые</option>
          </select>
        </div>

        {applications.length > 0 ? (
          <div className="applications-table">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Клиент</th>
                  <th>Участок</th>
                  <th>Услуга</th>
                  <th>Сообщение</th>
                  <th>Статус</th>
                  <th>Дата</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id}>
                    <td>{app.id}</td>
                    <td>{app.company_name || 'Клиент'}</td>
                    <td>{app.land_title || `#${app.land_id}`}</td>
                    <td>{app.service_name || `#${app.service_id}`}</td>
                    <td className="message-cell">{app.message || '—'}</td>
                    <td><span className={`status-badge status-${app.status}`}>{statusLabel(app.status)}</span></td>
                    <td>{new Date(app.created_at).toLocaleDateString('ru-RU')}</td>
                    <td className="actions-cell">
                      {app.status === 'pending' && (
                        <>
                          <button className="btn-sm btn-accept" onClick={() => handleStatusChange(app.id, 'accepted')}>Принять</button>
                          <button className="btn-sm btn-reject" onClick={() => handleStatusChange(app.id, 'rejected')}>Отклонить</button>
                        </>
                      )}
                      {app.status === 'accepted' && (
                        <button className="btn-sm btn-primary" onClick={() => handleStatusChange(app.id, 'in_progress')}>Начать работу</button>
                      )}
                      {app.status === 'in_progress' && (
                        <button className="btn-sm btn-complete" onClick={() => handleStatusChange(app.id, 'completed')}>Завершить</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>Нет заявок{statusFilter ? ` со статусом «${statusLabel(statusFilter)}»` : ''}</p>
          </div>
        )}
      </section>
    </>
  )
}

// ============================================================
// Главный компонент кабинета
// ============================================================
export default function CabinetPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/auth')
  }

  const isCompany = user?.role === 'company'

  return (
    <div className="cabinet-page">
      <header className="cabinet-header">
        <div className="header-content">
          <h1>{isCompany ? 'Кабинет компании' : 'Личный кабинет'}</h1>
          <p>{isCompany ? 'Управление заявками и профилем компании' : 'Управление участками и планами развития'}</p>
        </div>
        <nav className="header-nav">
          <button onClick={() => navigate('/')} className="btn-secondary">На карту</button>
          <button onClick={() => navigate('/services')} className="btn-secondary">Услуги</button>
          <button onClick={() => navigate('/companies')} className="btn-secondary">Компании</button>
          <button onClick={handleLogout} className="btn-danger">Выход</button>
        </nav>
      </header>

      <div className="cabinet-content">
        {isCompany ? <CompanyCabinet /> : <UserCabinet />}
      </div>
    </div>
  )
}
