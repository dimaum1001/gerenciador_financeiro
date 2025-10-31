import { createContext, useContext } from 'react'
import axios from 'axios'

const ApiContext = createContext({})

const rawBaseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').trim()
const apiVersionPattern = /\/api\/v\d+$/i

const sanitizedBaseUrl = rawBaseUrl.replace(/\/+$/, '')
let apiPrefix = import.meta.env.VITE_API_PREFIX
  ? `/${import.meta.env.VITE_API_PREFIX.replace(/^\/+|\/+$/g, '')}`
  : '/api/v1'

if (apiPrefix === '/') {
  apiPrefix = ''
}

if (apiVersionPattern.test(sanitizedBaseUrl)) {
  apiPrefix = ''
} else if (!import.meta.env.VITE_API_PREFIX) {
  apiPrefix = '/api/v1'
}

// Configurar instância do axios
const api = axios.create({
  baseURL: sanitizedBaseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para requests
api.interceptors.request.use(
  (config) => {
    if (config.url && !/^https?:\/\//i.test(config.url)) {
      const normalizedPath = config.url.startsWith('/') ? config.url : `/${config.url}`
      if (apiPrefix && !normalizedPath.startsWith(`${apiPrefix}/`)) {
        config.url = `${apiPrefix}${normalizedPath}`
      } else {
        config.url = normalizedPath
      }
    }

    // Adicionar timestamp para evitar cache
    config.params = {
      ...config.params,
      _t: Date.now()
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para responses
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Se token expirou, redirecionar para login
    if (error.response?.status === 401) {
      localStorage.removeItem('finance_token')
      delete api.defaults.headers.common['Authorization']
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export function ApiProvider({ children }) {
  const value = {
    api
  }

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  )
}

export function useApi() {
  const context = useContext(ApiContext)
  if (!context) {
    throw new Error('useApi deve ser usado dentro de ApiProvider')
  }
  return context
}
