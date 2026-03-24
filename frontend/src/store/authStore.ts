import { create } from 'zustand'
import { User, LoginRequest, RegisterRequest } from '@/types'
import { authApi } from '@/api/auth'

interface AuthStore {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null

  register: (data: RegisterRequest) => Promise<void>
  login: (data: LoginRequest) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('access_token') || null,
  isLoading: false,
  error: null,

  register: async (data: RegisterRequest) => {
    set({ isLoading: true, error: null })
    try {
      // Register returns only user info, not tokens
      const result = await authApi.register(data)

      // After registration, automatically login with the same credentials
      const loginResult = await authApi.login({
        email: data.email,
        password: data.password
      })

      localStorage.setItem('access_token', loginResult.access_token)
      localStorage.setItem('refresh_token', loginResult.refresh_token)
      set({ token: loginResult.access_token, isLoading: false })

      // Load user data
      const user = await authApi.getMe()
      localStorage.setItem('user', JSON.stringify(user))
      set({ user })
    } catch (error: any) {
      const message = error.response?.data?.error || error.message || 'Ошибка регистрации'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  login: async (data: LoginRequest) => {
    set({ isLoading: true, error: null })
    try {
      const result = await authApi.login(data)
      localStorage.setItem('access_token', result.access_token)
      localStorage.setItem('refresh_token', result.refresh_token)
      set({ token: result.access_token, isLoading: false })

      // Load user data
      const user = await authApi.getMe()
      localStorage.setItem('user', JSON.stringify(user))
      set({ user })
    } catch (error: any) {
      const message = error.response?.data?.error || error.message || 'Ошибка входа'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    set({ user: null, token: null })
  },

  loadUser: async () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      set({ user: JSON.parse(savedUser) })
      return
    }

    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        set({ isLoading: true })
        const user = await authApi.getMe()
        localStorage.setItem('user', JSON.stringify(user))
        set({ user, isLoading: false })
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, token: null, isLoading: false })
      }
    }
  },
}))
