import { createContext, useContext, useState, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useApi } from './ApiContext'

const AuthContext = createContext({})

const formatLocalDateToISO = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const { api } = useApi()
  const queryClient = useQueryClient()

  // Verificar token salvo no localStorage
  useEffect(() => {
    const token = localStorage.getItem('finance_token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Verificar se o token Ǹ vǭlido
      api.get('/auth/me')
        .then(response => {
          setUser(response.data)
          preloadUserData()
        })
        .catch(() => {
          // Token invǭlido, remover
          localStorage.removeItem('finance_token')
          delete api.defaults.headers.common['Authorization']
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [api])

  const preloadUserData = () => {
    const now = new Date()
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth() + 1

    const startDateIso = formatLocalDateToISO(new Date(currentYear, currentMonth - 1, 1))
    const endDateIso = formatLocalDateToISO(new Date(currentYear, currentMonth, 0))

    const immediatePrefetches = [
      queryClient.prefetchQuery({
        queryKey: ['accounts'],
        queryFn: async () => {
          const response = await api.get('/accounts', { params: { limit: 500 } })
          return response.data.accounts ?? []
        },
      }),
      queryClient.prefetchQuery({
        queryKey: ['accounts', 'import'],
        queryFn: async () => {
          const response = await api.get('/accounts', { params: { limit: 500, skip: 0 } })
          return response.data.accounts ?? []
        },
      }),
      queryClient.prefetchQuery({
        queryKey: ['categories'],
        queryFn: async () => {
          const response = await api.get('/categories', { params: { limit: 500, parent_id: '' } })
          return response.data.categories ?? []
        },
      }),
      queryClient.prefetchQuery({
        queryKey: ['budgets'],
        queryFn: async () => {
          const response = await api.get('/budgets', { params: { limit: 500 } })
          return response.data.budgets ?? []
        },
      }),
      queryClient.prefetchQuery({
        queryKey: ['dashboard', 'summary', currentYear, currentMonth],
        queryFn: async () => {
          const response = await api.get('/dashboard/summary', { params: { year: currentYear, month: currentMonth } })
          return response.data
        },
      }),
      queryClient.prefetchQuery({
        queryKey: ['dashboard', 'recent-transactions', 5],
        queryFn: async () => {
          const response = await api.get('/dashboard/recent-transactions', { params: { limit: 5 } })
          return response.data ?? []
        },
      }),
      queryClient.prefetchQuery({
        queryKey: ['dashboard', 'budget-status', currentYear, currentMonth],
        queryFn: async () => {
          const response = await api.get('/dashboard/budget-status', { params: { year: currentYear, month: currentMonth } })
          return response.data
        },
      }),
    ]

    Promise.allSettled(immediatePrefetches)

    setTimeout(() => {
      queryClient
        .prefetchQuery({
          queryKey: ['transactions', startDateIso, endDateIso],
          queryFn: async () => {
            const response = await api.get('/transactions', {
              params: {
                limit: 1000,
                data_inicio: startDateIso,
                data_fim: endDateIso,
              },
            })
            return response.data.transactions ?? []
          },
        })
        .catch(() => {})
    }, 300)
  }

  const login = async (email, senha) => {
    try {
      const response = await api.post('/auth/login', { email, senha })
      const { access_token, user: userData } = response.data

      // Salvar token
      localStorage.setItem('finance_token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      queryClient.clear()

      setUser(userData)
      preloadUserData()
      return { success: true }
    } catch (error) {
      console.error('Erro ao fazer login:', error)
      const message = error.response?.data?.detail || 'Erro ao fazer login'
      return { success: false, error: message }
    }
  }

  const logout = () => {
    localStorage.removeItem('finance_token')
    delete api.defaults.headers.common['Authorization']
    queryClient.clear()
    setUser(null)
  }

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }))
  }

  const value = {
    user,
    loading,
    login,
    logout,
    updateUser,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider')
  }
  return context
}
