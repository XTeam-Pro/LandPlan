import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { LoginRequest, RegisterRequest } from '@/types'
import '../styles/AuthPage.css'

export default function AuthPage() {
  const navigate = useNavigate()
  const { login, register } = useAuthStore()
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Login form
  const [loginForm, setLoginForm] = useState<LoginRequest>({
    email: '',
    password: '',
  })

  // Register form
  const [registerForm, setRegisterForm] = useState<RegisterRequest>({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    role: 'user',
  })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await login(loginForm)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка входа')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await register(registerForm)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка регистрации')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <h1>Моя Земля</h1>

        <div className="auth-tabs">
          <button
            className={`tab ${tab === 'login' ? 'active' : ''}`}
            onClick={() => setTab('login')}
          >
            Вход
          </button>
          <button
            className={`tab ${tab === 'register' ? 'active' : ''}`}
            onClick={() => setTab('register')}
          >
            Регистрация
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {tab === 'login' ? (
          <form onSubmit={handleLogin} className="auth-form" autoComplete="off">
            <div className="form-group">
              <label>Электронная почта</label>
              <input
                type="email"
                name="login-email-off"
                autoComplete="off"
                value={loginForm.email}
                onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label>Пароль</label>
              <input
                type="password"
                name="login-pass-off"
                autoComplete="new-password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                required
                disabled={isLoading}
              />
            </div>

            <button type="submit" className="submit-btn" disabled={isLoading}>
              {isLoading ? 'Вход в процессе...' : 'Вход'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="auth-form" autoComplete="off">
            <div className="registration-info">
              <h3>Как зарегистрироваться</h3>
              <ol>
                <li>Заполните все обязательные поля ниже</li>
                <li>Выберите тип аккаунта: пользователь или компания</li>
                <li>Если вы регистрируете компанию, после регистрации потребуется подтверждение администратора</li>
                <li>После регистрации вы сможете размещать объявления и подавать заявки</li>
              </ol>
            </div>

            <div className="form-group">
              <label>Полное имя *</label>
              <input
                type="text"
                name="reg-name-off"
                autoComplete="off"
                value={registerForm.full_name}
                onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })}
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label>Электронная почта *</label>
              <input
                type="email"
                name="reg-email-off"
                autoComplete="off"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label>Пароль (минимум 8 символов) *</label>
              <input
                type="password"
                name="reg-pass-off"
                autoComplete="new-password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                required
                minLength={8}
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label>Телефон (опционально)</label>
              <input
                type="tel"
                name="reg-phone-off"
                autoComplete="off"
                value={registerForm.phone || ''}
                onChange={(e) => setRegisterForm({ ...registerForm, phone: e.target.value })}
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label>Тип аккаунта</label>
              <select
                value={registerForm.role}
                onChange={(e) =>
                  setRegisterForm({ ...registerForm, role: e.target.value as 'user' | 'company' })
                }
                disabled={isLoading}
              >
                <option value="user">Пользователь (ищу участок)</option>
                <option value="company">Компания (поставщик услуг)</option>
              </select>
              {registerForm.role === 'company' && (
                <small className="info-text">
                  Аккаунт компании будет активирован после подтверждения администратором.
                </small>
              )}
            </div>

            <button type="submit" className="submit-btn" disabled={isLoading}>
              {isLoading ? 'Регистрация в процессе...' : 'Регистрация'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
