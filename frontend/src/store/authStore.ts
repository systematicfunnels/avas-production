import { create } from 'zustand'
import { api } from '@/services/api'

interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: api.isAuthenticated(),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      await api.login(email, password)
      set({ isAuthenticated: true, isLoading: false })
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed'
      set({ error: message, isLoading: false })
      throw err
    }
  },

  logout: () => {
    api.logout()
    set({ isAuthenticated: false })
    window.location.href = '/login'
  },

  clearError: () => set({ error: null }),
}))
