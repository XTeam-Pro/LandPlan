import { useEffect, useState } from 'react'
import { ApplicationDetail, ApplicationStats } from '@/types'
import { applicationsApi } from '@/api/applications'
import '../../styles/ApplicationsList.css'

interface ApplicationsListProps {
  onRefresh?: () => void
}

const statusColors: Record<string, string> = {
  pending: '#ffa500',
  accepted: '#4169e1',
  in_progress: '#32cd32',
  completed: '#228b22',
  rejected: '#dc143c',
  cancelled: '#808080',
}

const statusLabels: Record<string, string> = {
  pending: 'В ожидании',
  accepted: 'Принято',
  in_progress: 'В процессе',
  completed: 'Завершено',
  rejected: 'Отклонено',
  cancelled: 'Отменено',
}

export default function ApplicationsList({ onRefresh }: ApplicationsListProps) {
  const [applications, setApplications] = useState<ApplicationDetail[]>([])
  const [stats, setStats] = useState<ApplicationStats | null>(null)
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadApplications = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [appList, appStats] = await Promise.all([
        applicationsApi.list(statusFilter),
        applicationsApi.getStats(),
      ])
      setApplications(appList.items)
      setStats(appStats)
    } catch (err: any) {
      const message = err.response?.data?.error || 'Ошибка загрузки заявок'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadApplications()
  }, [statusFilter])

  useEffect(() => {
    if (onRefresh) {
      onRefresh()
    }
  }, [])

  return (
    <div className="applications-list">
      <h3>Мои заявки</h3>

      {error && <div className="error-message">{error}</div>}

      {/* Stats */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Всего</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">В ожидании</span>
            <span className="stat-value">{stats.pending}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Принято</span>
            <span className="stat-value">{stats.accepted}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">В процессе</span>
            <span className="stat-value">{stats.in_progress}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Завершено</span>
            <span className="stat-value">{stats.completed}</span>
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="filter-controls">
        <select
          value={statusFilter || ''}
          onChange={(e) => setStatusFilter(e.target.value || undefined)}
          className="status-filter"
        >
          <option value="">Все статусы</option>
          <option value="pending">В ожидании</option>
          <option value="accepted">Принято</option>
          <option value="in_progress">В процессе</option>
          <option value="completed">Завершено</option>
          <option value="rejected">Отклонено</option>
          <option value="cancelled">Отменено</option>
        </select>
      </div>

      {/* Applications table */}
      {isLoading ? (
        <div className="loading-spinner">Загрузка заявок...</div>
      ) : applications.length > 0 ? (
        <div className="applications-table">
          <div className="table-header">
            <div className="col col-id">ID</div>
            <div className="col col-land">Участок</div>
            <div className="col col-service">Услуга</div>
            <div className="col col-company">Компания</div>
            <div className="col col-status">Статус</div>
            <div className="col col-date">Дата</div>
          </div>

          {applications.map((app) => (
            <div key={app.id} className="table-row">
              <div className="col col-id">#{app.id}</div>
              <div className="col col-land">{app.land_title || 'Н/Д'}</div>
              <div className="col col-service">{app.service_name || 'Н/Д'}</div>
              <div className="col col-company">{app.company_name || 'Н/Д'}</div>
              <div className="col col-status">
                <span
                  className="status-badge"
                  style={{ backgroundColor: statusColors[app.status] }}
                >
                  {statusLabels[app.status]}
                </span>
              </div>
              <div className="col col-date">
                {new Date(app.created_at).toLocaleDateString('ru-RU')}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-applications">Заявки не найдены.</p>
      )}

      <button onClick={loadApplications} className="refresh-btn" disabled={isLoading}>
        {isLoading ? 'Загрузка...' : 'Обновить'}
      </button>
    </div>
  )
}
