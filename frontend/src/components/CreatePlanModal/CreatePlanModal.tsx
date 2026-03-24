import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RecommendationsResponse, ServiceRecommendation } from '@/types'
import { landPlansApi } from '@/api/landPlans'
import '../../styles/CreatePlanModal.css'

interface CreatePlanModalProps {
  landId: number
  recommendations: RecommendationsResponse
  onClose: () => void
}

export default function CreatePlanModal({ landId, recommendations, onClose }: CreatePlanModalProps) {
  const navigate = useNavigate()
  const [selectedIds, setSelectedIds] = useState<Set<number>>(
    new Set(recommendations.services.filter(s => s.priority === 'critical').map(s => s.service_id))
  )
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const toggleService = (id: number) => {
    const next = new Set(selectedIds)
    if (next.has(id)) {
      next.delete(id)
    } else {
      next.add(id)
    }
    setSelectedIds(next)
  }

  const handleSubmit = async () => {
    if (selectedIds.size === 0) {
      setError('Выберите хотя бы одну услугу')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const plan = await landPlansApi.create({
        land_id: landId,
        selected_service_ids: Array.from(selectedIds),
      })
      navigate(`/plan/${plan.id}`)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка при создании плана')
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderGroup = (services: ServiceRecommendation[], label: string, badge: string) => {
    if (services.length === 0) return null
    return (
      <div className="plan-service-group">
        <h4>{label} <span className="badge">{badge}</span></h4>
        {services.map((svc) => (
          <label key={svc.service_id} className="plan-service-item">
            <input
              type="checkbox"
              checked={selectedIds.has(svc.service_id)}
              onChange={() => toggleService(svc.service_id)}
            />
            <div className="service-details">
              <span className="service-name">{svc.service_name}</span>
              <span className="service-reason">{svc.reason}</span>
            </div>
            <span className="step-order">Этап {svc.step_order}</span>
          </label>
        ))}
      </div>
    )
  }

  const critical = recommendations.services.filter(s => s.priority === 'critical')
  const recommended = recommendations.services.filter(s => s.priority === 'recommended')
  const optional = recommendations.services.filter(s => s.priority === 'optional')

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Создание плана развития</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          <p className="plan-intro">
            Выберите услуги, которые хотите включить в план развития вашего участка.
            Критически важные услуги выбраны по умолчанию.
          </p>

          {error && <div className="error-message">{error}</div>}

          {renderGroup(critical, 'Критически важно', 'Обязательно')}
          {renderGroup(recommended, 'Рекомендуется', 'Желательно')}
          {renderGroup(optional, 'Опционально', 'По желанию')}

          <div className="plan-summary">
            Выбрано услуг: <strong>{selectedIds.size}</strong>
          </div>

          <div className="modal-actions">
            <button className="btn-secondary" onClick={onClose}>Отмена</button>
            <button className="btn-primary" onClick={handleSubmit} disabled={isSubmitting || selectedIds.size === 0}>
              {isSubmitting ? 'Создание...' : 'Создать план'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
