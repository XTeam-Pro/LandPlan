import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import '../styles/CreateListingPage.css'

interface ListingForm {
  cadastral_number: string
  title: string
  description: string
  address: string
  latitude: string
  longitude: string
  region_name: string
  city_name: string
  price: string
  area: string
  land_category: string
  allowed_usage: string
  deal_type: string
  has_building: boolean
  contact_phone: string
  // Features
  has_water: boolean
  has_electricity: boolean
  has_gas: boolean
  has_roads: boolean
  boundaries_defined: boolean
  build_ready: boolean
}

const initialForm: ListingForm = {
  cadastral_number: '',
  title: '',
  description: '',
  address: '',
  latitude: '',
  longitude: '',
  region_name: '',
  city_name: '',
  price: '',
  area: '',
  land_category: '',
  allowed_usage: '',
  deal_type: 'purchase',
  has_building: false,
  contact_phone: '',
  has_water: false,
  has_electricity: false,
  has_gas: false,
  has_roads: false,
  boundaries_defined: false,
  build_ready: false,
}

export default function CreateListingPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [form, setForm] = useState<ListingForm>(initialForm)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showCadastralWarning, setShowCadastralWarning] = useState(false)

  const listingType = user?.role === 'company' ? 'agency' : 'owner'

  const handleChange = (field: keyof ListingForm, value: any) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (field === 'cadastral_number') {
      setShowCadastralWarning(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate cadastral number
    if (!form.cadastral_number.trim()) {
      setShowCadastralWarning(true)
      return
    }

    setIsSubmitting(true)
    try {
      const { default: apiClient } = await import('@/api/client')
      await apiClient.post('/api/v1/lands/user-listing', {
        ...form,
        latitude: parseFloat(form.latitude) || 0,
        longitude: parseFloat(form.longitude) || 0,
        price: form.price ? parseFloat(form.price) : null,
        area: form.area ? parseFloat(form.area) : null,
        listing_type: listingType,
        features: {
          has_water: form.has_water,
          has_electricity: form.has_electricity,
          has_gas: form.has_gas,
          has_roads: form.has_roads,
          boundaries_defined: form.boundaries_defined,
          build_ready: form.build_ready,
        },
      })
      alert('Объявление отправлено на модерацию!')
      navigate('/cabinet')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка при создании объявления')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="create-listing-page">
      <header className="page-header">
        <div className="header-content">
          <h1 className="logo-title" onClick={() => navigate('/')}>Моя Земля</h1>
        </div>
        <nav className="header-nav">
          <button onClick={() => navigate('/')} className="btn-secondary">На карту</button>
          <button onClick={() => navigate('/cabinet')} className="btn-secondary">Мой кабинет</button>
        </nav>
      </header>

      <div className="listing-form-container">
        <h2>
          Разместить объявление
          <span className={`listing-type-badge listing-${listingType}`}>
            {listingType === 'owner' ? 'от собственника' : 'от агентства'}
          </span>
        </h2>

        {error && <div className="error-message">{error}</div>}

        {/* Cadastral number warning */}
        {showCadastralWarning && (
          <div className="cadastral-warning">
            <h3>Кадастровый номер обязателен</h3>
            <p>
              Для публикации объявления необходимо указать кадастровый номер участка.
              Если у вас нет кадастрового номера, воспользуйтесь услугами кадастровых инженеров.
            </p>
            <button
              className="btn-primary"
              onClick={() => navigate('/services?category=4')}
            >
              Найти кадастрового инженера
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="listing-form">
          {/* Cadastral number — required first field */}
          <div className="form-section">
            <h3>Основные данные</h3>

            <div className="form-group required">
              <label>Кадастровый номер *</label>
              <input
                type="text"
                placeholder="XX:XX:XXXXXXX:XXX"
                value={form.cadastral_number}
                onChange={(e) => handleChange('cadastral_number', e.target.value)}
                required
              />
              <small>Обязательное поле. Без кадастрового номера объявление не будет опубликовано.</small>
            </div>

            <div className="form-group">
              <label>Название объявления *</label>
              <input
                type="text"
                placeholder="Например: Участок 10 соток ИЖС"
                value={form.title}
                onChange={(e) => handleChange('title', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Описание</label>
              <textarea
                placeholder="Подробное описание участка..."
                value={form.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={4}
              />
            </div>
          </div>

          {/* Location */}
          <div className="form-section">
            <h3>Местоположение</h3>

            <div className="form-group">
              <label>Адрес *</label>
              <input
                type="text"
                placeholder="Полный адрес участка"
                value={form.address}
                onChange={(e) => handleChange('address', e.target.value)}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Регион / Республика</label>
                <input
                  type="text"
                  placeholder="Московская область"
                  value={form.region_name}
                  onChange={(e) => handleChange('region_name', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Населённый пункт</label>
                <input
                  type="text"
                  placeholder="Химки"
                  value={form.city_name}
                  onChange={(e) => handleChange('city_name', e.target.value)}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Широта</label>
                <input
                  type="text"
                  placeholder="55.7558"
                  value={form.latitude}
                  onChange={(e) => handleChange('latitude', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Долгота</label>
                <input
                  type="text"
                  placeholder="37.6176"
                  value={form.longitude}
                  onChange={(e) => handleChange('longitude', e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Characteristics */}
          <div className="form-section">
            <h3>Характеристики</h3>

            <div className="form-row">
              <div className="form-group">
                <label>Цена (₽)</label>
                <input
                  type="number"
                  placeholder="Стоимость"
                  value={form.price}
                  onChange={(e) => handleChange('price', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Площадь (м²)</label>
                <input
                  type="number"
                  placeholder="Площадь участка"
                  value={form.area}
                  onChange={(e) => handleChange('area', e.target.value)}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Тип сделки</label>
                <select value={form.deal_type} onChange={(e) => handleChange('deal_type', e.target.value)}>
                  <option value="purchase">Продажа</option>
                  <option value="lease">Аренда</option>
                  <option value="rent">Сдача в наём</option>
                </select>
              </div>
              <div className="form-group">
                <label>Категория земли</label>
                <select value={form.land_category} onChange={(e) => handleChange('land_category', e.target.value)}>
                  <option value="">Не указано</option>
                  <option value="residential">Жилая</option>
                  <option value="commercial">Коммерческая</option>
                  <option value="agricultural">Сельскохозяйственная</option>
                  <option value="industrial">Промышленная</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Вид разрешённого использования</label>
              <input
                type="text"
                placeholder="Например: ИЖС, ЛПХ, садоводство..."
                value={form.allowed_usage}
                onChange={(e) => handleChange('allowed_usage', e.target.value)}
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={form.has_building}
                  onChange={(e) => handleChange('has_building', e.target.checked)}
                />
                На участке есть дом / строение
              </label>
            </div>
          </div>

          {/* Features / Communications */}
          <div className="form-section">
            <h3>Коммуникации</h3>
            <div className="features-checkboxes">
              {[
                { key: 'has_water', label: 'Водоснабжение' },
                { key: 'has_electricity', label: 'Электричество' },
                { key: 'has_gas', label: 'Газ' },
                { key: 'has_roads', label: 'Дорога' },
                { key: 'boundaries_defined', label: 'Границы определены' },
                { key: 'build_ready', label: 'Готов к строительству' },
              ].map(({ key, label }) => (
                <label key={key} className="feature-checkbox">
                  <input
                    type="checkbox"
                    checked={(form as any)[key]}
                    onChange={(e) => handleChange(key as keyof ListingForm, e.target.checked)}
                  />
                  {label}
                </label>
              ))}
            </div>
          </div>

          {/* Contact */}
          <div className="form-section">
            <h3>Контакты</h3>
            <div className="form-group">
              <label>Телефон для связи</label>
              <input
                type="tel"
                placeholder="+7 (___) ___-__-__"
                value={form.contact_phone}
                onChange={(e) => handleChange('contact_phone', e.target.value)}
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={() => navigate(-1)}>
              Отмена
            </button>
            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Отправка...' : 'Разместить объявление'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
