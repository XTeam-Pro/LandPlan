import { RecommendationsResponse } from '@/types'
import '../../styles/RecommendationsBlock.css'

interface RecommendationsBlockProps {
  recommendations: RecommendationsResponse
  onCreatePlan?: () => void
}

export default function RecommendationsBlock({
  recommendations,
  onCreatePlan,
}: RecommendationsBlockProps) {
  const critical = recommendations.services.filter((s) => s.priority === 'critical')
  const recommended = recommendations.services.filter((s) => s.priority === 'recommended')
  const optional = recommendations.services.filter((s) => s.priority === 'optional')

  return (
    <div className="recommendations-block">
      <h3>Рекомендуемые услуги для вашего плана развития</h3>
      <p className="recommendations-summary">{recommendations.summary}</p>

      {critical.length > 0 && (
        <div className="recommendations-section critical">
          <div className="section-header">
            <h4>🔴 Критически важно ({critical.length})</h4>
            <span className="badge">Обязательно</span>
          </div>
          <ul className="recommendations-list">
            {critical.map((service) => (
              <li key={service.service_id} className="recommendation-item">
                <span className="service-name">{service.service_name}</span>
                <span className="reason">{service.reason}</span>
                <span className="order">Этап {service.step_order}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {recommended.length > 0 && (
        <div className="recommendations-section recommended">
          <div className="section-header">
            <h4>🟡 Рекомендуется ({recommended.length})</h4>
            <span className="badge">Желательно</span>
          </div>
          <ul className="recommendations-list">
            {recommended.map((service) => (
              <li key={service.service_id} className="recommendation-item">
                <span className="service-name">{service.service_name}</span>
                <span className="reason">{service.reason}</span>
                <span className="order">Этап {service.step_order}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {optional.length > 0 && (
        <div className="recommendations-section optional">
          <div className="section-header">
            <h4>🟢 Опционально ({optional.length})</h4>
            <span className="badge">По желанию</span>
          </div>
          <ul className="recommendations-list">
            {optional.map((service) => (
              <li key={service.service_id} className="recommendation-item">
                <span className="service-name">{service.service_name}</span>
                <span className="reason">{service.reason}</span>
                <span className="order">Этап {service.step_order}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {onCreatePlan && (
        <button onClick={onCreatePlan} className="create-plan-btn">
          Создать план развития
        </button>
      )}
    </div>
  )
}
