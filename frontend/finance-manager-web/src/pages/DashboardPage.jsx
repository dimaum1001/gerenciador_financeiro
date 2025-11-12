import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import LoadingSpinner from '@/components/ui/loading-spinner'
import { useApi } from '@/contexts/ApiContext'
import { formatCurrency } from '@/lib/formatters'
import { normalizeTransactionType, getField } from '@/lib/api-locale'
import { RefreshCcw } from 'lucide-react'

export default function DashboardPage() {
  const { api } = useApi()

  const accountsQuery = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const response = await api.get('/accounts', { params: { limit: 500 } })
      return response.data.accounts ?? []
    },
  })

  const transactionsQuery = useQuery({
    queryKey: ['transactions'],
    queryFn: async () => {
      const response = await api.get('/transactions', { params: { limit: 500 } })
      return response.data.transactions ?? []
    },
  })

  const budgetsQuery = useQuery({
    queryKey: ['budgets'],
    queryFn: async () => {
      const response = await api.get('/budgets', { params: { limit: 500 } })
      return response.data.budgets ?? []
    },
  })

  const categoriesQuery = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get('/categories', { params: { limit: 500 } })
      return response.data.categories ?? []
    },
  })

  const refreshAll = () => {
    accountsQuery.refetch()
    transactionsQuery.refetch()
    budgetsQuery.refetch()
    categoriesQuery.refetch()
  }

  const accounts = accountsQuery.data ?? []
  const transactions = transactionsQuery.data ?? []
  const budgets = budgetsQuery.data ?? []
  const categories = categoriesQuery.data ?? []

  const now = new Date()
  const currentMonth = now.getMonth() + 1
  const currentYear = now.getFullYear()

  const resumo = useMemo(() => {
    const saldoTotal = accounts.reduce((sum, account) => sum + Number(account.saldo_atual ?? account.saldo_inicial ?? 0), 0)

    const monthTransactions = transactions.filter((tx) => {
      if (!tx.data_lancamento) return false
      const [year, month] = tx.data_lancamento.split('-').map(Number)
      return year === currentYear && month === currentMonth
    })

    const receitasMes = monthTransactions
      .filter((tx) => normalizeTransactionType(tx.tipo) === 'receita')
      .reduce((sum, tx) => sum + Number(tx.valor || 0), 0)

    const despesasMes = monthTransactions
      .filter((tx) => normalizeTransactionType(tx.tipo) === 'despesa')
      .reduce((sum, tx) => sum + Number(tx.valor || 0), 0)

    const saldoMes = receitasMes - despesasMes

    return {
      saldoTotal,
      receitasMes,
      despesasMes,
      saldoMes,
    }
  }, [accounts, transactions, currentMonth, currentYear])

  const ultimasTransacoes = useMemo(
    () => transactions
      .slice()
      .sort((a, b) => (a.data_lancamento < b.data_lancamento ? 1 : -1))
      .slice(0, 5),
    [transactions]
  )

  const orcamentosResumo = useMemo(
    () =>
      budgets.map((budget) => {
        const utilizado = Number(budget.valor_realizado || 0)
        const planejado = Number(budget.valor_planejado || 0)
        const percentual = planejado > 0 ? Math.min((utilizado / planejado) * 100, 999) : 0
                    const categoriaId = getField(budget, 'categoria_id', 'category_id')
                    const categoria = categories.find((cat) => cat.id === categoriaId)
        return {
          ...budget,
          percentual,
          restante: planejado - utilizado,
          categoriaNome: categoria?.nome || 'Categoria removida',
        }
      }),
    [budgets, categories]
  )

  const isLoading =
    accountsQuery.isLoading || transactionsQuery.isLoading || budgetsQuery.isLoading || categoriesQuery.isLoading

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Resumo em tempo real das suas finanças.</p>
        </div>
        <Button variant="outline" onClick={refreshAll}>
          <RefreshCcw className="h-4 w-4 mr-2" /> Atualizar
        </Button>
      </div>

      {isLoading ? (
        <div className="py-16 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Saldo total"
              description="Soma de todas as contas"
              value={formatCurrency(resumo.saldoTotal)}
            />
            <StatCard
              title="Receitas do mês"
              description="Entradas registradas"
              value={formatCurrency(resumo.receitasMes)}
            />
            <StatCard
              title="Despesas do mês"
              description="Saídas registradas"
              value={formatCurrency(resumo.despesasMes)}
            />
            <StatCard
              title="Saldo do mês"
              description="Receitas - despesas"
              value={formatCurrency(resumo.saldoMes)}
            />
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
                        <div className={`text-sm font-medium ${tipoNormalizado === 'receita' ? 'text-green-600' : tipoNormalizado === 'despesa' ? 'text-red-600' : 'text-blue-600'}`}>
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
                <CardDescription>Progresso das metas definidas.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {orcamentosResumo.length === 0 ? (
                  <p className="text-muted-foreground text-sm">Nenhum orçamento cadastrado.</p>
                ) : (
                  orcamentosResumo.map((budget) => (
                    <div key={budget.id} className="border rounded-md px-3 py-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold">{budget.categoriaNome}</div>
                          <div className="text-xs text-muted-foreground">
                            {budget.ano}/{String(budget.mes).padStart(2, '0')}
                          </div>
                        </div>
                        <div className="text-sm font-medium">
                          {formatCurrency(budget.valor_realizado)} / {formatCurrency(budget.valor_planejado)}
                        </div>
                      </div>
                      <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full ${budget.percentual >= 100 ? 'bg-red-500' : budget.percentual >= 80 ? 'bg-yellow-500' : 'bg-green-500'}`}
                          style={{ width: `${Math.min(budget.percentual, 100)}%` }}
                        />
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        {budget.percentual.toFixed(1)}% utilizado • Restante {formatCurrency(budget.restante)}
                      </div>
                    </div>
                  ))
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
