import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { LandPlanDetail, Company } from '@/types'
import { landPlansApi } from '@/api/landPlans'
import { companiesApi } from '@/api/companies'
import ApplicationModal from '@/components/ApplicationModal/ApplicationModal'
import '../styles/PlanDetailPage.css'

export default function PlanDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [plan, setPlan] = useState<LandPlanDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [stepCompanies, setStepCompanies] = useState<Record<number, Company[]>>({})
  const [expandedStep, setExpandedStep] = useState<number | null>(null)
  const [applicationTarget, setApplicationTarget] = useState<{
    serviceId: number; serviceName: string; companyId: number; companyName: string
  } | null>(null)

  useEffect(() => {
    if (!id) return
    const load = async () => {
      try {
        const data = await landPlansApi.getById(parseInt(id))
        setPlan(data)
      } catch (err) {
        console.error('Failed to load plan', err)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [id])

  const loadCompaniesForStep = async (serviceId: number) => {
    if (stepCompanies[serviceId]) return
    try {
      const response = await companiesApi.getByService(serviceId)
      setStepCompanies((prev) => ({ ...prev, [serviceId]: response.items || [] }))
    } catch {
      setStepCompanies((prev) => ({ ...prev, [serviceId]: [] }))
    }
  }

  const toggleStepCompanies = (stepId: number, serviceId: number) => {
    if (expandedStep === stepId) {
      setExpandedStep(null)
    } else {
      setExpandedStep(stepId)
      loadCompaniesForStep(serviceId)
    }
  }

  const handleCompleteStep = async (stepId: number) => {
    try {
      await landPlansApi.completeStep(stepId)
      // Reload
      if (id) {
        const data = await landPlansApi.getById(parseInt(id))
        setPlan(data)
      }
    } catch (err: any) {
      alert(err.response?.data?.error || 'Ошибка')
    }
  }

  const statusLabel = (s: string) => {
    const map: Record<string, string> = {
      pending: 'Ожидает',
      in_progress: 'В работе',
      completed: 'Завершён',
      skipped: 'Пропущен',
      active: 'Активен',
    }
    return map[s] || s
  }

  if (isLoading) {
    return <div className="plan-detail-page"><div className="loading-spinner">Загрузка плана...</div></div>
  }

  if (!plan) {
    return (
      <div className="plan-detail-page">
        <div className="error-message">План не найден</div>
        <button onClick={() => navigate('/cabinet')} className="btn-primary">В кабинет</button>
      </div>
    )
  }

  const completedSteps = plan.steps.filter(s => s.status === 'completed').length
  const totalSteps = plan.steps.length
  const progress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0

  return (
    <div className="plan-detail-page">
      <header className="detail-header">
        <button onClick={() => navigate('/cabinet')} className="btn-back">← В кабинет</button>
        <h1>План развития</h1>
      </header>

      <div className="plan-info">
        <div className="plan-meta">
          <span className={`status-badge status-${plan.status}`}>{statusLabel(plan.status)}</span>
          <span className="plan-date">Создан: {new Date(plan.created_at).toLocaleDateString('ru-RU')}</span>
        </div>
        {plan.summary && <p className="plan-summary">{plan.summary}</p>}

        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
          <span className="progress-text">{completedSteps} / {totalSteps} этапов ({progress}%)</span>
        </div>
      </div>

      <div className="steps-list">
        <h2>Этапы плана</h2>
        {plan.steps.sort((a, b) => a.order - b.order).map((step) => (
          <div key={step.id} className={`step-card step-${step.status}`}>
            <div className="step-order">Этап {step.order}</div>
            <div className="step-info">
              <h3>{step.title || step.service_name || `Услуга #${step.service_id}`}</h3>
              {step.description && <p>{step.description}</p>}
            </div>
            <div className="step-actions">
              <span className={`status-badge status-${step.status}`}>{statusLabel(step.status)}</span>
              {(step.status === 'pending' || step.status === 'in_progress') && (
                <>
                  <button
                    className="btn-small btn-secondary"
                    onClick={() => toggleStepCompanies(step.id, step.service_id)}
                  >
                    {expandedStep === step.id ? 'Скрыть компании' : 'Выбрать компанию'}
                  </button>
                  <button
                    className="btn-small btn-primary"
                    onClick={() => handleCompleteStep(step.id)}
                  >
                    Завершить
                  </button>
                </>
              )}
            </div>

            {/* Companies list for this step */}
            {expandedStep === step.id && (
              <div className="step-companies">
                <h4>Доступные компании</h4>
                {!stepCompanies[step.service_id] ? (
                  <p className="loading-text">Загрузка...</p>
                ) : stepCompanies[step.service_id].length === 0 ? (
                  <p className="no-companies-text">Нет доступных компаний для этой услуги</p>
                ) : (
                  <div className="companies-grid">
                    {stepCompanies[step.service_id].map((company) => (
                      <div key={company.id} className="step-company-card">
                        <div className="step-company-info">
                          <span
                            className="company-link"
                            onClick={() => navigate(`/company/${company.id}`)}
                          >
                            {company.public_name}
                          </span>
                          <span className="company-rating-sm">
                            {'★'.repeat(Math.round(company.rating))} {company.rating.toFixed(1)}
                          </span>
                        </div>
                        <button
                          className="btn-small btn-primary"
                          onClick={() => setApplicationTarget({
                            serviceId: step.service_id,
                            serviceName: step.title || step.service_name || `Услуга #${step.service_id}`,
                            companyId: company.id,
                            companyName: company.public_name,
                          })}
                        >
                          Обратиться
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <button onClick={() => navigate(`/land/${plan.land_id}`)} className="btn-secondary" style={{ marginTop: '1rem' }}>
        К участку
      </button>

      {/* Application Modal */}
      {applicationTarget && plan && (
        <ApplicationModal
          landId={plan.land_id}
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
    </div>
  )
}
