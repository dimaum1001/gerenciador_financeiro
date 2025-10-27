
import { useMemo, useState } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { eachMonthOfInterval, startOfMonth, subMonths, format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import LoadingSpinner from '@/components/ui/loading-spinner'
import { Progress } from '@/components/ui/progress'
import { formatCurrency } from '@/lib/formatters'
import { useCashFlow, useCategoriesSummary, useAccountsBalance, useBudgetStatus } from '@/hooks/useApi'

const pieColors = ['#2563eb', '#22c55e', '#ef4444', '#f97316', '#a855f7', '#0ea5e9']

function buildCategoryDataset(items = []) {
  return (items ?? [])
    .map((item, index) => {
      const name = item?.category ?? item?.categoria ?? 'Sem categoria'
      const rawValue = item?.value ?? item?.valor ?? 0
      const value = Math.abs(Number(rawValue))

      if (!Number.isFinite(value) || value <= 0) {
        return null
      }

      const rawPercentage = Number(item?.percentage ?? item?.percentual ?? 0)
      const percentage = Number.isFinite(rawPercentage) ? rawPercentage : 0
      const color = item?.color ?? item?.cor ?? pieColors[index % pieColors.length]
      const quantity = Number(item?.quantity ?? item?.quantidade ?? 0)

      return {
        key: `${name}-${index}`,
        name,
        value,
        percentage,
        color,
        quantity: Number.isFinite(quantity) ? quantity : 0,
      }
    })
    .filter(Boolean)
    .sort((a, b) => b.value - a.value)
    .map((item, index) => ({
      ...item,
      color: item.color ?? pieColors[index % pieColors.length],
    }))
}

function CategoryPieTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null
  }

  const { name, value, percentage } = payload[0].payload

  return (
    <div className="rounded-lg border bg-background/95 px-3 py-2 text-xs shadow-sm">
      <p className="font-semibold">{name}</p>
      <p>{formatCurrency(value ?? 0)}</p>
      <p className="text-muted-foreground">{`${Number(percentage ?? 0).toFixed(1)}%`}</p>
    </div>
  )
}

function CategoryList({ data, total }) {
  if (!data?.length) {
    return null
  }

  return (
    <div className="space-y-4">
      <div className="flex items-baseline justify-between text-sm text-muted-foreground">
        <span>Total no periodo</span>
        <span className="font-semibold text-foreground">{formatCurrency(total ?? 0)}</span>
      </div>
      <div className="space-y-3">
        {data.map((item) => {
          const percentageLabel = `${Number(item.percentage ?? 0).toFixed(1)}%`
          const progressValue = Math.max(0, Math.min(Number(item.percentage ?? 0), 100))
          const launchCount = item.quantity === 1 ? '1 lancamento' : `${item.quantity} lancamentos`

          return (
            <div key={item.key} className="flex gap-4 rounded-lg border p-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-md text-xs font-semibold uppercase text-white"
                style={{ backgroundColor: item.color }}
              >
                {item.name.slice(0, 2)}
              </div>
              <div className="flex-1">
                <div className="flex items-baseline justify-between text-sm font-medium">
                  <span>{item.name}</span>
                  <span>{formatCurrency(item.value)}</span>
                </div>
                <Progress value={progressValue} className="mt-3 h-2" />
                <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{launchCount}</span>
                  <span>{percentageLabel}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function SectionState({ loading, error, emptyMessage, children }) {
  if (loading) {
    return (
      <div className="flex h-[260px] items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return <p className="text-sm text-red-500">Nao foi possível carregar os dados.</p>
  }

  if (emptyMessage) {
    return <p className="text-sm text-muted-foreground">{emptyMessage}</p>
  }

  return children
}

export default function ReportsPage() {
  const [categoryTab, setCategoryTab] = useState('expense')
  const [categoryMonths, setCategoryMonths] = useState(3)

  const today = new Date()
  const [budgetMonth, setBudgetMonth] = useState(() => format(startOfMonth(today), 'yyyy-MM'))
  const [budgetYear, budgetMonthNumber] = budgetMonth.split('-').map((value) => Number(value))

  const { data: cashFlow, isLoading: cashFlowLoading, isError: cashFlowError } = useCashFlow(12)
  const { data: expenseCategories, isLoading: expenseLoading, isError: expenseError } = useCategoriesSummary('expense', categoryMonths)
  const { data: incomeCategories, isLoading: incomeLoading, isError: incomeError } = useCategoriesSummary('income', categoryMonths)
  const { data: accountsBalance, isLoading: accountsLoading, isError: accountsError } = useAccountsBalance()
  const { data: budgetStatus, isLoading: budgetLoading, isError: budgetError } = useBudgetStatus(budgetYear, budgetMonthNumber)

  const cashFlowData = useMemo(() => {
    if (!cashFlow) return []
    return cashFlow.map((item) => ({
      name: item.month_name ?? `${String(item.month).padStart(2, '0')}/${item.year}`,
      income: Number(item.income ?? 0),
      expenses: Math.abs(Number(item.expenses ?? 0)),
      balance: Number(item.balance ?? 0),
    }))
  }, [cashFlow])

  const expenseData = useMemo(() => buildCategoryDataset(expenseCategories), [expenseCategories])
  const incomeData = useMemo(() => buildCategoryDataset(incomeCategories), [incomeCategories])
  const expenseTotal = useMemo(() => expenseData.reduce((sum, item) => sum + item.value, 0), [expenseData])
  const incomeTotal = useMemo(() => incomeData.reduce((sum, item) => sum + item.value, 0), [incomeData])

  const accountsData = useMemo(() => {
    if (!accountsBalance) return []
    return accountsBalance.map((item) => ({
      name: item.name,
      balance: Number(item.balance ?? 0),
      percentage: Number(item.percentage ?? 0),
    }))
  }, [accountsBalance])

  const budgetData = useMemo(() => {
    if (!budgetStatus) return []
    return (budgetStatus.budgets ?? []).map((item) => ({
      name: item.category ?? 'Orcamento',
      planned: Number(item.planned ?? 0),
      spent: Number(item.spent ?? 0),
      percentage: Number(item.percentage ?? 0),
    }))
  }, [budgetStatus])

  const budgetMonthOptions = useMemo(() => {
    const end = startOfMonth(today)
    const start = subMonths(end, 11)
    return eachMonthOfInterval({ start, end }).reverse().map((date) => {
      const value = format(date, 'yyyy-MM')
      const label = format(date, "MMMM 'de' yyyy", { locale: ptBR })
      return {
        value,
        label: label.charAt(0).toUpperCase() + label.slice(1),
      }
    })
  }, [today])

  const selectedBudgetLabel = useMemo(() => {
    const option = budgetMonthOptions.find((opt) => opt.value === budgetMonth)
    return option?.label ?? ''
  }, [budgetMonthOptions, budgetMonth])

  const selectedCategories = categoryTab === 'expense' ? expenseData : incomeData


  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Relatorios</h1>
        <p className="text-muted-foreground">Visualize tendencias e distribuicoes das suas finanças.</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Fluxo de caixa (12 meses)</CardTitle>
            <CardDescription>Receitas, despesas e saldo acumulado.</CardDescription>
          </CardHeader>
          <CardContent>
            <SectionState loading={cashFlowLoading} error={cashFlowError} emptyMessage={cashFlowData.length ? null : 'Sem dados de fluxo para o periodo.'}>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={cashFlowData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(value ?? 0)} />
                  <Legend />
                  <Area type="monotone" dataKey="income" stroke="#22c55e" fill="#22c55e" fillOpacity={0.25} name="Receitas" />
                  <Area type="monotone" dataKey="expenses" stroke="#ef4444" fill="#ef4444" fillOpacity={0.25} name="Despesas" />
                  <Area type="monotone" dataKey="balance" stroke="#2563eb" fill="#2563eb" fillOpacity={0.15} name="Saldo" />
                </AreaChart>
              </ResponsiveContainer>
            </SectionState>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Saldo por conta</CardTitle>
            <CardDescription>Distribuicao do saldo atual entre as contas ativas.</CardDescription>
          </CardHeader>
          <CardContent>
            <SectionState loading={accountsLoading} error={accountsError} emptyMessage={accountsData.length ? null : 'Nenhuma conta ativa para exibir.'}>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={accountsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(value ?? 0)} />
                  <Bar dataKey="balance" fill="#1d4ed8" radius={[4, 4, 0, 0]} name="Saldo" />
                </BarChart>
              </ResponsiveContainer>
            </SectionState>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <CardTitle>Distribuicao por categoria</CardTitle>
            <CardDescription>Receitas e despesas agrupadas por categoria.</CardDescription>
          </div>
          <div className="flex items-center gap-4">
            <Select value={String(categoryMonths)} onValueChange={(value) => setCategoryMonths(Number(value))}>
              <SelectTrigger className="w-[170px]">
                <SelectValue placeholder="Periodo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Ultimo mes</SelectItem>
                <SelectItem value="3">Ultimos 3 meses</SelectItem>
                <SelectItem value="6">Ultimos 6 meses</SelectItem>
                <SelectItem value="12">Ultimos 12 meses</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={categoryTab} onValueChange={setCategoryTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="expense">Despesas</TabsTrigger>
              <TabsTrigger value="income">Receitas</TabsTrigger>
            </TabsList>
            <TabsContent value="expense">
              <SectionState
                loading={expenseLoading}
                error={expenseError}
                emptyMessage={expenseData.length ? null : 'Sem dados de categorias para o periodo.'}
              >
                <div className="flex flex-col gap-6 lg:flex-row">
                  <div className="h-[280px] w-full lg:w-1/2">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={expenseData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={110} paddingAngle={4}>
                          {expenseData.map((entry, index) => (
                            <Cell key={entry.key} fill={entry.color || pieColors[index % pieColors.length]} strokeWidth={1} />
                          ))}
                        </Pie>
                        <Tooltip content={<CategoryPieTooltip />} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex-1">
                    <CategoryList data={expenseData} total={expenseTotal} />
                  </div>
                </div>
              </SectionState>
            </TabsContent>
            <TabsContent value="income">
              <SectionState
                loading={incomeLoading}
                error={incomeError}
                emptyMessage={incomeData.length ? null : 'Sem dados de categorias para o periodo.'}
              >
                <div className="flex flex-col gap-6 lg:flex-row">
                  <div className="h-[280px] w-full lg:w-1/2">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={incomeData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={110} paddingAngle={4}>
                          {incomeData.map((entry, index) => (
                            <Cell key={entry.key} fill={entry.color || pieColors[index % pieColors.length]} strokeWidth={1} />
                          ))}
                        </Pie>
                        <Tooltip content={<CategoryPieTooltip />} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex-1">
                    <CategoryList data={incomeData} total={incomeTotal} />
                  </div>
                </div>
              </SectionState>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <CardTitle>Orcamentos</CardTitle>
            <CardDescription>{`Planejado vs realizado em ${selectedBudgetLabel}`}</CardDescription>
          </div>
          <Select value={budgetMonth} onValueChange={setBudgetMonth}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Selecione o mes" />
            </SelectTrigger>
            <SelectContent>
              {budgetMonthOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          <SectionState
            loading={budgetLoading}
            error={budgetError}
            emptyMessage={budgetData.length ? null : 'Nenhum orcamento cadastrado para o periodo.'}
          >
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={budgetData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" hide={budgetData.length > 6} />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value ?? 0)} />
                <Legend />
                <Bar dataKey="planned" fill="#2563eb" name="Planejado" radius={[4, 4, 0, 0]} />
                <Bar dataKey="spent" fill="#f97316" name="Realizado" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </SectionState>
        </CardContent>
      </Card>
    </div>
  )
}
