import { useNavigate } from 'react-router-dom'
import '../styles/PlaceholderPage.css'

export default function GovernmentSalesPage() {
  const navigate = useNavigate()

  return (
    <div className="placeholder-page">
      <header className="page-header">
        <div className="header-content">
          <h1 className="logo-title" onClick={() => navigate('/')}>Моя Земля</h1>
        </div>
        <nav className="header-nav">
          <button onClick={() => navigate('/')} className="btn-secondary">На карту</button>
        </nav>
      </header>

      <div className="placeholder-content">
        <div className="placeholder-icon">🏢</div>
        <h2>Государственные торги</h2>
        <p className="placeholder-status">Раздел в разработке</p>
        <p className="placeholder-desc">
          Здесь будут представлены земельные участки, реализуемые государственными органами.
          Следите за обновлениями.
        </p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Вернуться на главную
        </button>
      </div>
    </div>
  )
}
