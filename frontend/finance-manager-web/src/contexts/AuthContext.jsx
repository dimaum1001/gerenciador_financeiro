import { createContext, useContext, useState, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useApi } from './ApiContext'

const AuthContext = createContext({})

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

  const login = async (email, senha) => {
    try {
      const response = await api.post('/auth/login', { email, senha })
      const { access_token, user: userData } = response.data

      // Salvar token
      localStorage.setItem('finance_token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      queryClient.clear()

      setUser(userData)
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
