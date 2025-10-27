import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  CreditCard,
  PiggyBank,
  Target,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw
} from 'lucide-react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'
import {
  useDashboardSummary,
  useCashFlow,
  useCategoriesSummary,
  useAccountsBalance,
  useUpcomingBills,
  useBudgetStatus
} from '@/hooks/useApi'
import LoadingSpinner from '@/components/ui/loading-spinner'

function StatCard({ title, value, change, trend, icon: Icon, color, loading = false }) {
  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <Icon className={`h-4 w-4 ${color}`} />
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <LoadingSpinner size="sm" />
            <span className="text-sm text-muted-foreground">Carregando...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${color}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className="flex items-center text-xs text-muted-foreground">
          {trend === 'up' ? (
            <ArrowUpRight className="h-3 w-3 text-green-500 mr-1" />
          ) : (
            <ArrowDownRight className="h-3 w-3 text-red-500 mr-1" />
          )}
          <span className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
            {change}
          </span>
          <span className="ml-1">vs mês anterior</span>
        </div>
      </CardContent>
    </Card>
  )
}

function FluxoCaixaChart() {
  const { data: cashFlow, isLoading, error } = useCashFlow(6)

  if (isLoading) {
    return (
      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>Fluxo de Caixa</CardTitle>
          <CardDescription>Receitas vs Despesas dos últimos 6 meses</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[300px]">
          <LoadingSpinner size="lg" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>Fluxo de Caixa</CardTitle>
          <CardDescription>Receitas vs Despesas dos últimos 6 meses</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[300px]">
          <div className="text-center">
            <p className="text-muted-foreground">Erro ao carregar dados</p>
            <Button variant="outline" size="sm" className="mt-2">
              <RefreshCw className="h-4 w-4 mr-2" />
              Tentar novamente
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="col-span-4">
      <CardHeader>
        <CardTitle>Fluxo de Caixa</CardTitle>
        <CardDescription>
          Receitas vs Despesas dos últimos 6 meses
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={cashFlow}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month_name" />
            <YAxis />
            <Tooltip 
              formatter={(value) => [`R$ ${value.toLocaleString()}`, '']}
              labelFormatter={(label) => `Mês: ${label}`}
            />
            <Area 
              type="monotone" 
              dataKey="income" 
              stackId="1"
              stroke="#10b981" 
              fill="#10b981" 
              fillOpacity={0.6}
              name="Receitas"
            />
            <Area 
              type="monotone" 
              dataKey="expenses" 
              stackId="2"
              stroke="#ef4444" 
              fill="#ef4444" 
              fillOpacity={0.6}
              name="Despesas"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function GastosCategoriasChart() {
  const { data: categories, isLoading, error } = useCategoriesSummary('expense', 1)

  if (isLoading) {
    return (
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Gastos por Categoria</CardTitle>
          <CardDescription>Distribuição das despesas do mês atual</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[300px]">
          <LoadingSpinner size="lg" />
        </CardContent>
      </Card>
    )
  }

  if (error || !categories?.length) {
    return (
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Gastos por Categoria</CardTitle>
          <CardDescription>Distribuição das despesas do mês atual</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[300px]">
          <p className="text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>Gastos por Categoria</CardTitle>
        <CardDescription>
          Distribuição das despesas do mês atual
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={categories}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={5}
              dataKey="amount"
              nameKey="name"
            >
              {categories.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `R$ ${value.toLocaleString()}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function SaldosContas() {
  const { data: accounts, isLoading } = useAccountsBalance()

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Saldos por Conta</CardTitle>
          <CardDescription>Distribuição do patrimônio</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <LoadingSpinner size="lg" />
        </CardContent>
      </Card>
    )
  }

  if (!accounts?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Saldos por Conta</CardTitle>
          <CardDescription>Distribuição do patrimônio</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <p className="text-muted-foreground">Nenhuma conta encontrada</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Saldos por Conta</CardTitle>
        <CardDescription>
          Distribuição do patrimônio
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {accounts.map((account, index) => (
          <div key={index} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: account.color }}
                />
                <span className="text-sm font-medium">{account.name}</span>
              </div>
              <span className="text-sm font-bold">
                R$ {account.balance.toLocaleString()}
              </span>
            </div>
            <Progress value={account.percentage} className="h-2" />
            <div className="text-xs text-muted-foreground text-right">
              {account.percentage.toFixed(1)}% do total
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

function ProximosVencimentos() {
  const { data: bills, isLoading } = useUpcomingBills(30)

  const getStatusIcon = (status, daysUntil) => {
    if (status === 'overdue' || daysUntil < 0) {
      return <AlertTriangle className="h-4 w-4 text-red-500" />
    } else if (daysUntil <= 3) {
      return <Clock className="h-4 w-4 text-yellow-500" />
    } else {
      return <CheckCircle className="h-4 w-4 text-green-500" />
    }
  }

  const getStatusBadge = (status, daysUntil) => {
    if (status === 'overdue' || daysUntil < 0) {
      return <Badge variant="destructive">Vencido</Badge>
    } else if (daysUntil <= 3) {
      return <Badge variant="secondary">Próximo</Badge>
    } else {
      return <Badge variant="outline">Pendente</Badge>
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Próximos Vencimentos</CardTitle>
          <CardDescription>Contas a pagar nos próximos dias</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <LoadingSpinner size="lg" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Próximos Vencimentos</CardTitle>
        <CardDescription>
          Contas a pagar nos próximos dias
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {bills?.length ? bills.slice(0, 4).map((item, index) => (
          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
            <div className="flex items-center gap-3">
              {getStatusIcon(item.status, item.days_until)}
              <div>
                <div className="font-medium">{item.description}</div>
                <div className="text-sm text-muted-foreground">
                  {item.days_until < 0 
                    ? `Venceu há ${Math.abs(item.days_until)} dia${Math.abs(item.days_until) !== 1 ? 's' : ''}`
                    : `Vence em ${item.days_until} dia${item.days_until !== 1 ? 's' : ''}`
                  }
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold">R$ {item.amount.toLocaleString()}</div>
              {getStatusBadge(item.status, item.days_until)}
            </div>
          </div>
        )) : (
          <p className="text-center text-muted-foreground py-4">
            Nenhum vencimento próximo
          </p>
        )}
      </CardContent>
    </Card>
  )
}

function OrcamentosResumo() {
  const now = new Date()
  const { data: budgetStatus, isLoading } = useBudgetStatus(now.getFullYear(), now.getMonth() + 1)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Orçamentos do Mês</CardTitle>
          <CardDescription>Acompanhamento das metas mensais</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <LoadingSpinner size="lg" />
        </CardContent>
      </Card>
    )
  }

  if (!budgetStatus?.budgets?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Orçamentos do Mês</CardTitle>
          <CardDescription>Acompanhamento das metas mensais</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <p className="text-muted-foreground">Nenhum orçamento configurado</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Orçamentos do Mês</CardTitle>
        <CardDescription>
          Acompanhamento das metas mensais
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {budgetStatus.budgets.slice(0, 4).map((budget, index) => {
          const getProgressColor = (percentual) => {
            if (percentual >= 100) return 'bg-red-500'
            if (percentual >= 80) return 'bg-yellow-500'
            return 'bg-green-500'
          }

          return (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{budget.category}</span>
                <span className="text-sm">
                  R$ {budget.spent.toLocaleString()} / R$ {budget.planned.toLocaleString()}
                </span>
              </div>
              <div className="relative">
                <Progress value={budget.percentage} className="h-2" />
                <div 
                  className={`absolute top-0 left-0 h-2 rounded-full transition-all ${getProgressColor(budget.percentage)}`}
                  style={{ width: `${Math.min(budget.percentage, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{budget.percentage.toFixed(1)}% utilizado</span>
                <span>
                  R$ {budget.remaining.toLocaleString()} restante
                </span>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useDashboardSummary()

  // Preparar dados dos cards
  const cards = summary ? [
    {
      title: 'Saldo Total',
      value: `R$ ${summary.total_balance.toLocaleString()}`,
      change: '+8,2%', // Seria calculado baseado em dados históricos
      trend: 'up',
      icon: DollarSign,
      color: 'text-green-600'
    },
    {
      title: 'Receitas do Mês',
      value: `R$ ${summary.monthly_income.toLocaleString()}`,
      change: `${summary.income_change >= 0 ? '+' : ''}${summary.income_change.toFixed(1)}%`,
      trend: summary.income_change >= 0 ? 'up' : 'down',
      icon: TrendingUp,
      color: 'text-blue-600'
    },
    {
      title: 'Despesas do Mês',
      value: `R$ ${summary.monthly_expenses.toLocaleString()}`,
      change: `${summary.expenses_change >= 0 ? '+' : ''}${summary.expenses_change.toFixed(1)}%`,
      trend: summary.expenses_change <= 0 ? 'up' : 'down', // Menos despesa é melhor
      icon: TrendingDown,
      color: 'text-red-600'
    },
    {
      title: 'Economia do Mês',
      value: `R$ ${summary.monthly_savings.toLocaleString()}`,
      change: '+12,8%', // Seria calculado
      trend: 'up',
      icon: PiggyBank,
      color: 'text-green-600'
    }
  ] : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Visão geral das suas finanças em tempo real
        </p>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {summaryLoading ? (
          // Skeleton loading
          Array.from({ length: 4 }).map((_, index) => (
            <StatCard 
              key={index} 
              title="Carregando..." 
              value="..." 
              change="..." 
              trend="up" 
              icon={DollarSign} 
              color="text-gray-400"
              loading={true}
            />
          ))
        ) : (
          cards.map((card, index) => (
            <StatCard key={index} {...card} />
          ))
        )}
      </div>

      {/* Gráficos principais */}
      <div className="grid gap-4 md:grid-cols-7">
        <FluxoCaixaChart />
        <GastosCategoriasChart />
      </div>

      {/* Seção inferior */}
      <div className="grid gap-4 md:grid-cols-3">
        <SaldosContas />
        <ProximosVencimentos />
        <OrcamentosResumo />
      </div>
    </div>
  )
}
