import { useState } from 'react'
import { ApplicationCreateRequest } from '@/types'
import { applicationsApi } from '@/api/applications'
import '../../styles/ApplicationModal.css'

interface ApplicationModalProps {
  landId: number
  serviceId: number
  serviceName: string
  companyId: number
  companyName: string
  onClose: () => void
  onSuccess: () => void
}

export default function ApplicationModal({
  landId,
  serviceId,
  serviceName,
  companyId,
  companyName,
  onClose,
  onSuccess,
}: ApplicationModalProps) {
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      const data: ApplicationCreateRequest = {
        land_id: landId,
        service_id: serviceId,
        company_id: companyId,
        message: message || undefined,
      }
      await applicationsApi.create(data)
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка при создании заявки')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Подать заявку</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          <div className="application-info">
            <div className="info-row">
              <span className="label">Услуга:</span>
              <span className="value">{serviceName}</span>
            </div>
            <div className="info-row">
              <span className="label">Компания:</span>
              <span className="value">{companyName}</span>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Сообщение для подрядчика (опционально)</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Опишите вашу задачу, пожелания, сроки..."
                rows={4}
              />
            </div>

            <div className="modal-actions">
              <button type="button" className="btn-secondary" onClick={onClose}>
                Отмена
              </button>
              <button type="submit" className="btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Отправка...' : 'Отправить заявку'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
