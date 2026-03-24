import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Company } from '@/types'
import { companiesApi } from '@/api/companies'
import '../styles/CompaniesPage.css'

export default function CompaniesPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [companies, setCompanies] = useState<Company[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [serviceId, setServiceId] = useState(searchParams.get('service_id') || '')

  const fetchCompanies = async () => {
    setIsLoading(true)
    try {
      const filters: Record<string, any> = {}
      if (search) filters.search_query = search
      if (serviceId) filters.service_id = parseInt(serviceId)
      const result = await companiesApi.list(filters)
      setCompanies(result.items || [])
      setTotal(result.total || 0)
    } catch (err) {
      console.error('Failed to load companies', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCompanies()
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchCompanies()
  }

  const verificationLabel = (s: string) => {
    if (s === 'verified') return 'Проверена'
    if (s === 'pending') return 'На проверке'
    return 'Не проверена'
  }

  return (
    <div className="companies-page">
      <header className="page-header">
        <div className="header-content">
          <h1>Каталог компаний</h1>
          <p>Найдено подрядчиков: {total}</p>
        </div>
        <nav className="header-nav">
          <button onClick={() => navigate('/')} className="btn-secondary">На карту</button>
          <button onClick={() => navigate('/services')} className="btn-secondary">Услуги</button>
        </nav>
      </header>

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Поиск компаний..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <input
          type="number"
          placeholder="ID услуги"
          value={serviceId}
          onChange={(e) => setServiceId(e.target.value)}
          style={{ width: '120px' }}
        />
        <button type="submit" className="btn-primary">Найти</button>
      </form>

      {isLoading ? (
        <div className="loading-spinner">Загрузка компаний...</div>
      ) : (
        <div className="companies-grid">
          {companies.length > 0 ? companies.map((company) => (
            <div
              key={company.id}
              className="company-card"
              onClick={() => navigate(`/company/${company.id}`)}
            >
              <div className="company-card-header">
                <h3>{company.public_name}</h3>
                <span className={`verification-badge ${company.verification_status}`}>
                  {verificationLabel(company.verification_status)}
                </span>
              </div>
              {company.description && (
                <p className="company-desc">{company.description.slice(0, 120)}...</p>
              )}
              <div className="company-card-footer">
                <div className="rating">
                  {'★'.repeat(Math.round(company.rating))}{'☆'.repeat(5 - Math.round(company.rating))}
                  <span>{company.rating.toFixed(1)} ({company.reviews_count})</span>
                </div>
                <button className="btn-small">Подробнее</button>
              </div>
            </div>
          )) : (
            <p className="no-results">Компании не найдены</p>
          )}
        </div>
      )}
    </div>
  )
}
