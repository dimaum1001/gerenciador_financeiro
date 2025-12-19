import { useMemo, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import LoadingSpinner from '@/components/ui/loading-spinner'
import { useApi } from '@/contexts/ApiContext'
import { useDashboardSummary, useRecentTransactions } from '@/hooks/useApi'
import { formatCurrency } from '@/lib/formatters'
import { getField, normalizeTransactionType } from '@/lib/api-locale'
import { RefreshCcw } from 'lucide-react'

export default function DashboardPage() {
  const { api } = useApi()

  const now = new Date()
  const currentMonth = now.getMonth() + 1
  const currentYear = now.getFullYear()

  const [selectedMonth, setSelectedMonth] = useState(currentMonth)
  const [selectedYear, setSelectedYear] = useState(currentYear)

  const monthOptions = useMemo(
    () =>
      Array.from({ length: 12 }, (_, index) => {
        const monthNumber = index + 1
        const label = new Date(2020, index, 1).toLocaleString('pt-BR', { month: 'long' })
        return {
          value: monthNumber,
          label: label.charAt(0).toUpperCase() + label.slice(1),
        }
      }),
    [],
  )

  const yearOptions = useMemo(() => {
    const yearsBefore = 5
    const yearsAfter = 2
    const startYear = currentYear - yearsBefore
    return Array.from({ length: yearsBefore + yearsAfter + 1 }, (_, index) => startYear + index).reverse()
  }, [currentYear])

  const selectedMonthLabel =
    monthOptions.find((option) => option.value === selectedMonth)?.label ?? String(selectedMonth).padStart(2, '0')
  const selectedPeriodLabel = `${selectedMonthLabel} de ${selectedYear}`

  const summaryQuery = useDashboardSummary(selectedYear, selectedMonth, { placeholderData: keepPreviousData })
  const recentTransactionsQuery = useRecentTransactions(5)

  const categoriesQuery = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get('/categories', { params: { limit: 500, parent_id: '' } })
      return response.data.categories ?? []
    },
  })

  const budgetsQuery = useQuery({
    queryKey: ['budgets'],
    queryFn: async () => {
      const response = await api.get('/budgets', { params: { limit: 500 } })
      return response.data.budgets ?? []
    },
  })

  const refreshAll = () => {
    summaryQuery.refetch()
    recentTransactionsQuery.refetch()
    categoriesQuery.refetch()
    budgetsQuery.refetch()
  }

  const resumo = useMemo(() => {
    const summary = summaryQuery.data
    const saldoTotal = Number(summary?.total_balance ?? 0)
    const receitasMes = Number(summary?.monthly_income ?? 0)
    const despesasMes = Number(summary?.monthly_expenses ?? 0)

    return {
      saldoTotal,
      receitasMes,
      despesasMes,
      saldoMes: receitasMes - despesasMes,
    }
  }, [summaryQuery.data])

  const categories = categoriesQuery.data ?? []
  const budgets = budgetsQuery.data ?? []

  const categoriesById = useMemo(() => Object.fromEntries(categories.map((category) => [category.id, category])), [categories])
  const nowPeriodKey = currentYear * 12 + currentMonth

  const ultimasTransacoes = recentTransactionsQuery.data ?? []

  const orcamentosResumo = useMemo(() => {
    return budgets
      .filter((budget) => budget?.ativo !== false)
      .filter((budget) => {
        const ano = Number(budget?.ano ?? 0)
        const mes = Number(budget?.mes ?? 0)
        return ano * 12 + mes >= nowPeriodKey
      })
      .sort((a, b) => {
        const periodA = Number(a?.ano ?? 0) * 12 + Number(a?.mes ?? 0)
        const periodB = Number(b?.ano ?? 0) * 12 + Number(b?.mes ?? 0)
        if (periodA !== periodB) return periodA - periodB

        const catA = categoriesById[getField(a, 'categoria_id', 'category_id')]?.nome ?? ''
        const catB = categoriesById[getField(b, 'categoria_id', 'category_id')]?.nome ?? ''
        return catA.localeCompare(catB)
      })
      .map((budget) => {
        const planned = Number(budget?.valor_planejado ?? 0)
        const spent = Number(budget?.valor_realizado ?? 0)
        const percentage = planned > 0 ? Math.min((spent / planned) * 100, 999) : 0
        const categoryId = getField(budget, 'categoria_id', 'category_id')
        const category = categoriesById[categoryId]

        return {
          id: budget.id,
          period: budget?.periodo_display ?? `${String(budget?.mes ?? '').padStart(2, '0')}/${budget?.ano ?? ''}`,
          category: category?.nome ?? 'Categoria',
          planned,
          spent,
          remaining: Number(budget?.valor_restante ?? planned - spent),
          percentage,
        }
      })
  }, [budgets, categoriesById, nowPeriodKey])

  const isLoading = summaryQuery.isLoading || recentTransactionsQuery.isLoading

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Resumo em tempo real das suas finanças.</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div className="flex gap-2">
            <div className="min-w-[160px]">
              <Select value={String(selectedMonth)} onValueChange={(value) => setSelectedMonth(Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="Mês" />
                </SelectTrigger>
                <SelectContent>
                  {monthOptions.map((option) => (
                    <SelectItem key={option.value} value={String(option.value)}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="min-w-[120px]">
              <Select value={String(selectedYear)} onValueChange={(value) => setSelectedYear(Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="Ano" />
                </SelectTrigger>
                <SelectContent>
                  {yearOptions.map((year) => (
                    <SelectItem key={year} value={String(year)}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button variant="outline" onClick={refreshAll}>
            <RefreshCcw className="h-4 w-4 mr-2" /> Atualizar
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="py-16 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard title="Saldo total" description="Soma de todas as contas" value={formatCurrency(resumo.saldoTotal)} />
            <StatCard title="Receitas do mês" description={`Entradas em ${selectedPeriodLabel}`} value={formatCurrency(resumo.receitasMes)} />
            <StatCard title="Despesas do mês" description={`Saídas em ${selectedPeriodLabel}`} value={formatCurrency(resumo.despesasMes)} />
            <StatCard title="Saldo do mês" description={`Receitas - despesas em ${selectedPeriodLabel}`} value={formatCurrency(resumo.saldoMes)} />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Últimas transações</CardTitle>
                <CardDescription>As cinco movimentações mais recentes.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {ultimasTransacoes.length === 0 ? (
                  <p className="text-muted-foreground text-sm">Nenhuma transação registrada ainda.</p>
                ) : (
                  ultimasTransacoes.map((tx) => {
                    const tipoNormalizado = normalizeTransactionType(tx.tipo)
                    const valor = Number(tx.valor || 0)
                    return (
                      <div key={tx.id} className="flex items-center justify-between border rounded-md px-3 py-2">
                        <div>
                          <div className="font-semibold">{tx.descricao}</div>
                          <div className="text-xs text-muted-foreground">
                            {tx.data_lancamento} • {tipoNormalizado === 'receita' ? 'Receita' : tipoNormalizado === 'despesa' ? 'Despesa' : 'Transferência'}
                          </div>
                        </div>
                        <div
                          className={`text-sm font-medium ${
                            tipoNormalizado === 'receita' ? 'text-green-600' : tipoNormalizado === 'despesa' ? 'text-red-600' : 'text-blue-600'
                          }`}
                        >
                          {formatCurrency(tipoNormalizado === 'despesa' ? valor * -1 : valor)}
                        </div>
                      </div>
                    )
                  })
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Orçamentos</CardTitle>
                <CardDescription>Orçamentos ativos e futuros (não expirados).</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {budgetsQuery.isLoading || categoriesQuery.isLoading ? (
                  <div className="py-8 flex justify-center">
                    <LoadingSpinner />
                  </div>
                ) : orcamentosResumo.length === 0 ? (
                  <p className="text-muted-foreground text-sm">Nenhum orçamento ativo/futuro cadastrado.</p>
                ) : (
                  orcamentosResumo.map((budget) => {
                    const percentual = Number(budget.percentage ?? 0)
                    const planejado = Number(budget.planned ?? 0)
                    const realizado = Number(budget.spent ?? 0)
                    const restante = Number(budget.remaining ?? planejado - realizado)

                    return (
                      <div key={budget.id} className="border rounded-md px-3 py-2">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-semibold">{budget.category}</div>
                            <div className="text-xs text-muted-foreground">{budget.period}</div>
                          </div>
                          <div className="text-sm font-medium">
                            {formatCurrency(realizado)} / {formatCurrency(planejado)}
                          </div>
                        </div>
                        <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              percentual >= 100 ? 'bg-red-500' : percentual >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${Math.min(percentual, 100)}%` }}
                          />
                        </div>
                        <div className="mt-1 text-xs text-muted-foreground">
                          {percentual.toFixed(1)}% utilizado • Restante {formatCurrency(restante)}
                        </div>
                      </div>
                    )
                  })
                )}
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}

function StatCard({ title, description, value }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  )
}
