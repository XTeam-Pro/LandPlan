import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CompanyDetail, ReviewDetail, CompanyReviewsStatsSchema } from '@/types'
import { companiesApi } from '@/api/companies'
import { reviewsApi } from '@/api/reviews'
import { useAuthStore } from '@/store/authStore'
import '../styles/CompanyDetailPage.css'

export default function CompanyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [company, setCompany] = useState<CompanyDetail | null>(null)
  const [reviews, setReviews] = useState<ReviewDetail[]>([])
  const [stats, setStats] = useState<CompanyReviewsStatsSchema | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Review form
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [reviewRating, setReviewRating] = useState(5)
  const [reviewText, setReviewText] = useState('')
  const [reviewSubmitting, setReviewSubmitting] = useState(false)

  useEffect(() => {
    if (!id) return
    const load = async () => {
      try {
        const companyData = await companiesApi.getById(parseInt(id))
        setCompany(companyData)
        try {
          const reviewsData = await reviewsApi.getCompanyReviews(parseInt(id))
          setReviews(reviewsData.reviews || [])
          setStats(reviewsData.stats || null)
        } catch { /* reviews may not exist yet */ }
      } catch (err) {
        console.error('Failed to load company', err)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [id])

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    setReviewSubmitting(true)
    try {
      await reviewsApi.create(parseInt(id), {
        company_id: parseInt(id),
        rating: reviewRating,
        text: reviewText,
      })
      setShowReviewForm(false)
      setReviewText('')
      setReviewRating(5)
      // Reload reviews
      const reviewsData = await reviewsApi.getCompanyReviews(parseInt(id))
      setReviews(reviewsData.reviews || [])
      setStats(reviewsData.stats || null)
    } catch (err: any) {
      alert(err.response?.data?.error || 'Ошибка при отправке отзыва')
    } finally {
      setReviewSubmitting(false)
    }
  }

  if (isLoading) {
    return <div className="company-detail-page"><div className="loading-spinner">Загрузка...</div></div>
  }

  if (!company) {
    return (
      <div className="company-detail-page">
        <div className="error-message">Компания не найдена</div>
        <button onClick={() => navigate('/companies')} className="btn-primary">К списку компаний</button>
      </div>
    )
  }

  return (
    <div className="company-detail-page">
      <header className="detail-header">
        <button onClick={() => navigate('/companies')} className="btn-back">← Назад к списку</button>
      </header>

      <div className="company-content">
        <main className="main-column">
          <div className="company-profile">
            <div className="company-title-row">
              <h1>{company.public_name}</h1>
              <span className={`verification-badge ${company.verification_status}`}>
                {company.verification_status === 'verified' ? 'Проверена' : company.verification_status === 'pending' ? 'На проверке' : 'Не проверена'}
              </span>
            </div>

            {company.legal_name !== company.public_name && (
              <p className="legal-name">Юр. лицо: {company.legal_name}</p>
            )}

            {company.description && <p className="company-description">{company.description}</p>}

            <div className="contact-info">
              <h3>Контакты</h3>
              <div className="info-grid">
                {company.contact_phone && (
                  <div className="info-item">
                    <span className="label">Телефон</span>
                    <span className="value">{company.contact_phone}</span>
                  </div>
                )}
                {company.contact_email && (
                  <div className="info-item">
                    <span className="label">Email</span>
                    <span className="value">{company.contact_email}</span>
                  </div>
                )}
                {company.website && (
                  <div className="info-item">
                    <span className="label">Сайт</span>
                    <span className="value">{company.website}</span>
                  </div>
                )}
              </div>
            </div>

            {company.services && company.services.length > 0 && (
              <div className="company-services">
                <h3>Услуги компании</h3>
                <div className="services-list">
                  {company.services.map((svc) => (
                    <div key={svc.id} className="service-tag">
                      <span>{svc.service_name}</span>
                      {svc.base_price_from && (
                        <span className="price">от {svc.base_price_from.toLocaleString()} ₽</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Reviews section */}
          <div className="reviews-section">
            <div className="reviews-header">
              <h3>Отзывы ({stats?.total_reviews || 0})</h3>
              <div className="rating-summary">
                <span className="avg-rating">{'★'.repeat(Math.round(company.rating))}</span>
                <span>{company.rating.toFixed(1)}</span>
              </div>
              {user && (
                <button
                  className="btn-primary"
                  onClick={() => setShowReviewForm(!showReviewForm)}
                >
                  {showReviewForm ? 'Отмена' : 'Написать отзыв'}
                </button>
              )}
            </div>

            {showReviewForm && (
              <form className="review-form" onSubmit={handleSubmitReview}>
                <div className="rating-input">
                  <label>Оценка:</label>
                  <div className="stars">
                    {[1, 2, 3, 4, 5].map((n) => (
                      <span
                        key={n}
                        className={`star ${n <= reviewRating ? 'active' : ''}`}
                        onClick={() => setReviewRating(n)}
                      >
                        ★
                      </span>
                    ))}
                  </div>
                </div>
                <textarea
                  placeholder="Ваш отзыв..."
                  value={reviewText}
                  onChange={(e) => setReviewText(e.target.value)}
                  rows={4}
                />
                <button type="submit" className="btn-primary" disabled={reviewSubmitting}>
                  {reviewSubmitting ? 'Отправка...' : 'Отправить отзыв'}
                </button>
              </form>
            )}

            <div className="reviews-list">
              {reviews.length > 0 ? reviews.map((review) => (
                <div key={review.id} className="review-card">
                  <div className="review-header">
                    <span className="reviewer">{review.user_name || 'Пользователь'}</span>
                    <span className="review-rating">{'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}</span>
                    <span className="review-date">{new Date(review.created_at).toLocaleDateString('ru-RU')}</span>
                  </div>
                  {review.text && <p className="review-text">{review.text}</p>}
                </div>
              )) : (
                <p className="no-reviews">Отзывов пока нет</p>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
