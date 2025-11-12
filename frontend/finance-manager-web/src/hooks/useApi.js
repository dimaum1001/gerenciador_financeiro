import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useApi } from '@/contexts/ApiContext'
import { useToast } from '@/hooks/use-toast'

// Hook para listar dados com paginação
export function useApiList(endpoint, options = {}) {
  const { api } = useApi()
  const { 
    page = 1, 
    limit = 50, 
    filters = {}, 
    enabled = true,
    ...queryOptions 
  } = options

  return useQuery({
    queryKey: [endpoint, { page, limit, ...filters }],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: (page - 1) * limit,
        limit: limit.toString(),
        ...filters
      })
      
      const response = await api.get(`${endpoint}?${params}`)
      return response.data
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutos
    ...queryOptions
  })
}

// Hook para obter item específico
export function useApiGet(endpoint, id, options = {}) {
  const { api } = useApi()
  const { enabled = !!id, ...queryOptions } = options

  return useQuery({
    queryKey: [endpoint, id],
    queryFn: async () => {
      const response = await api.get(`${endpoint}/${id}`)
      return response.data
    },
    enabled,
    staleTime: 5 * 60 * 1000,
    ...queryOptions
  })
}

// Hook para criar item
export function useApiCreate(endpoint, options = {}) {
  const { api } = useApi()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const { onSuccess, onError, ...mutationOptions } = options

  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post(endpoint, data)
      return response.data
    },
    onSuccess: (data, variables) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: [endpoint] })
      
      toast({
        title: "Sucesso",
        description: "Item criado com sucesso",
      })
      
      onSuccess?.(data, variables)
    },
    onError: (error, variables) => {
      const message = error.response?.data?.detail || 'Erro ao criar item'
      
      toast({
        title: "Erro",
        description: message,
        variant: "destructive",
      })
      
      onError?.(error, variables)
    },
    ...mutationOptions
  })
}

// Hook para atualizar item
export function useApiUpdate(endpoint, options = {}) {
  const { api } = useApi()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const { onSuccess, onError, ...mutationOptions } = options

  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.put(`${endpoint}/${id}`, data)
      return response.data
    },
    onSuccess: (data, variables) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: [endpoint] })
      queryClient.invalidateQueries({ queryKey: [endpoint, variables.id] })
      
      toast({
        title: "Sucesso",
        description: "Item atualizado com sucesso",
      })
      
      onSuccess?.(data, variables)
    },
    onError: (error, variables) => {
      const message = error.response?.data?.detail || 'Erro ao atualizar item'
      
      toast({
        title: "Erro",
        description: message,
        variant: "destructive",
      })
      
      onError?.(error, variables)
    },
    ...mutationOptions
  })
}

// Hook para excluir item
export function useApiDelete(endpoint, options = {}) {
  const { api } = useApi()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const { onSuccess, onError, ...mutationOptions } = options

  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`${endpoint}/${id}`)
      return id
    },
    onSuccess: (id, variables) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: [endpoint] })
      queryClient.removeQueries({ queryKey: [endpoint, id] })
      
      toast({
        title: "Sucesso",
        description: "Item excluído com sucesso",
      })
      
      onSuccess?.(id, variables)
    },
    onError: (error, variables) => {
      const message = error.response?.data?.detail || 'Erro ao excluir item'
      
      toast({
        title: "Erro",
        description: message,
        variant: "destructive",
      })
      
      onError?.(error, variables)
    },
    ...mutationOptions
  })
}

// Hooks específicos para cada entidade

// Accounts
export const useAccounts = (options) => useApiList('/accounts', options)
export const useAccount = (id, options) => useApiGet('/accounts', id, options)
export const useCreateAccount = (options) => useApiCreate('/accounts', options)
export const useUpdateAccount = (options) => useApiUpdate('/accounts', options)
export const useDeleteAccount = (options) => useApiDelete('/accounts', options)

// Categories
export const useCategories = (options) => useApiList('/categories', options)
export const useCategory = (id, options) => useApiGet('/categories', id, options)
export const useCreateCategory = (options) => useApiCreate('/categories', options)
export const useUpdateCategory = (options) => useApiUpdate('/categories', options)
export const useDeleteCategory = (options) => useApiDelete('/categories', options)

// Transactions
export const useTransactions = (options) => useApiList('/transactions', options)
export const useTransaction = (id, options) => useApiGet('/transactions', id, options)
export const useCreateTransaction = (options) => useApiCreate('/transactions', options)
export const useUpdateTransaction = (options) => useApiUpdate('/transactions', options)
export const useDeleteTransaction = (options) => useApiDelete('/transactions', options)

// Budgets
export const useBudgets = (options) => useApiList('/budgets', options)
export const useBudget = (id, options) => useApiGet('/budgets', id, options)
export const useCreateBudget = (options) => useApiCreate('/budgets', options)
export const useUpdateBudget = (options) => useApiUpdate('/budgets', options)
export const useDeleteBudget = (options) => useApiDelete('/budgets', options)

// Dashboard
export const useDashboardSummary = (options = {}) => {
  const { api } = useApi()
  
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: async () => {
      const response = await api.get('/dashboard/summary')
      return response.data
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
    ...options
  })
}

export const useCashFlow = (months = 6, options = {}) => {
  const { api } = useApi()
  
  return useQuery({
    queryKey: ['dashboard', 'cash-flow', months],
    queryFn: async () => {
      const response = await api.get(`/dashboard/cash-flow?months=${months}`)
      return response.data
    },
    staleTime: 5 * 60 * 1000,
    ...options
  })
}

export const useCategoriesSummary = (tipo, paramsOrMonths = {}, options = {}) => {
  const { api } = useApi()
  const now = new Date()

  let params = paramsOrMonths
  let queryOptions = options

  if (typeof paramsOrMonths === 'number') {
    params = { months: paramsOrMonths }
    queryOptions = options || {}
  } else if (paramsOrMonths && typeof paramsOrMonths === 'object' && !Array.isArray(paramsOrMonths)) {
    params = paramsOrMonths
  } else if (!paramsOrMonths) {
    params = {}
  }

  const { months, year, month } = params
  const useMonths = typeof months === 'number' && months > 0
  const effectiveYear = typeof year === 'number' ? year : now.getFullYear()
  const effectiveMonth = typeof month === 'number' ? month : undefined

  const buildSearchParams = () => {
    const searchParams = new URLSearchParams({ tipo })
    if (useMonths) {
      searchParams.set('months', String(months))
    } else {
      searchParams.set('year', String(effectiveYear))
      if (effectiveMonth) {
        searchParams.set('month', String(effectiveMonth))
      }
    }
    return searchParams.toString()
  }

  const queryKey = [
    'dashboard',
    'categories-summary',
    tipo,
    useMonths ? months : null,
    useMonths ? null : effectiveYear,
    useMonths ? null : effectiveMonth ?? null
  ]
  
  return useQuery({
    queryKey,
    queryFn: async () => {
      const response = await api.get(`/dashboard/categories-summary?${buildSearchParams()}`)
      return response.data
    },
    enabled: !!tipo,
    staleTime: 5 * 60 * 1000,
    ...queryOptions
  })
}

export const useAccountsBalance = (options = {}) => {
  const { api } = useApi()
  
  return useQuery({
    queryKey: ['dashboard', 'accounts-balance'],
    queryFn: async () => {
      const response = await api.get('/dashboard/accounts-balance')
      return response.data
    },
    staleTime: 2 * 60 * 1000,
    ...options
  })
}

export const useUpcomingBills = (days = 30, options = {}) => {
  const { api } = useApi()
  
  return useQuery({
    queryKey: ['dashboard', 'upcoming-bills', days],
    queryFn: async () => {
      const response = await api.get(`/dashboard/upcoming-bills?days=${days}`)
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
    ...options
  })
}

export const useBudgetStatus = (year, month, options = {}) => {
  const { api } = useApi()
  
  return useQuery({
    queryKey: ['dashboard', 'budget-status', year, month],
    queryFn: async () => {
      const response = await api.get(`/dashboard/budget-status?year=${year}&month=${month}`)
      return response.data
    },
    enabled: !!(year && month),
    staleTime: 5 * 60 * 1000,
    ...options
  })
}
