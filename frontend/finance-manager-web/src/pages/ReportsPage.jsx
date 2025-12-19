
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
import { startOfMonth, format } from 'date-fns'
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

function CategoryLegend({ data }) {
  if (!data?.length) return null

  return (
    <div className="mt-4 flex flex-wrap items-center justify-center gap-x-4 gap-y-2 px-2 text-xs md:text-sm">
      {data.map((item) => (
        <div key={item.key} className="flex items-center gap-2">
          <span className="inline-flex h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
          <span className="text-foreground/80">{item.name}</span>
        </div>
      ))}
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
  const [categoryTab, setCategoryTab] = useState('despesa')
  const [categoryMode, setCategoryMode] = useState('range')
  const [categoryMonths, setCategoryMonths] = useState(3)
  const today = new Date()
  const [categoryYear, setCategoryYear] = useState(today.getFullYear())
  const [cashFlowYear, setCashFlowYear] = useState(today.getFullYear())
  const [budgetYear, setBudgetYear] = useState(today.getFullYear())
  const [budgetMonth, setBudgetMonth] = useState(today.getMonth() + 1)

  const { data: cashFlow, isLoading: cashFlowLoading, isError: cashFlowError } = useCashFlow({ year: cashFlowYear })
  const categoryFilters = useMemo(() => {
    return categoryMode === 'range'
      ? { months: categoryMonths }
      : { year: categoryYear }
  }, [categoryMode, categoryMonths, categoryYear])
  const { data: expenseCategories, isLoading: expenseLoading, isError: expenseError } = useCategoriesSummary('despesa', categoryFilters)
  const { data: incomeCategories, isLoading: incomeLoading, isError: incomeError } = useCategoriesSummary('receita', categoryFilters)
  const { data: accountsBalance, isLoading: accountsLoading, isError: accountsError } = useAccountsBalance()
  const { data: budgetStatus, isLoading: budgetLoading, isError: budgetError } = useBudgetStatus(budgetYear, budgetMonth)

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
  const yearRangeOptions = useMemo(() => {
    const currentYear = today.getFullYear()
    const yearsBefore = 5
    const yearsAfter = 2
    const startYear = currentYear - yearsBefore
    return Array.from({ length: yearsBefore + yearsAfter + 1 }, (_, index) => startYear + index).reverse()
  }, [today])
  const categoryYearOptions = yearRangeOptions

  const cashFlowYearOptions = useMemo(() => {
    const currentYear = today.getFullYear()
    const yearsBefore = 5
    const yearsAfter = 2
    const startYear = currentYear - yearsBefore
    return Array.from({ length: yearsBefore + yearsAfter + 1 }, (_, index) => startYear + index).reverse()
  }, [today])

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

  const budgetYearOptions = useMemo(() => {
    const currentYear = today.getFullYear()
    const yearsBefore = 2
    const yearsAfter = 3
    const startYear = currentYear - yearsBefore
    return Array.from({ length: yearsBefore + yearsAfter + 1 }, (_, index) => startYear + index)
  }, [today])

  const budgetMonthOptions = useMemo(() => {
    return Array.from({ length: 12 }, (_, index) => {
      const monthDate = startOfMonth(new Date(2020, index, 1))
      const label = format(monthDate, 'MMMM', { locale: ptBR })
      return {
        value: index + 1,
        label: label.charAt(0).toUpperCase() + label.slice(1),
      }
    })
  }, [])

  const selectedBudgetLabel = useMemo(() => {
    const monthLabel = budgetMonthOptions.find((opt) => opt.value === budgetMonth)?.label ?? ''
    return monthLabel ? `${monthLabel} de ${budgetYear}` : `${budgetYear}`
  }, [budgetMonthOptions, budgetMonth, budgetYear])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Relatorios</h1>
        <p className="text-muted-foreground">Visualize tendencias e distribuicoes das suas finanças.</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <CardTitle>Fluxo de caixa</CardTitle>
              <CardDescription>{`Receitas, despesas e saldo de ${cashFlowYear}`}</CardDescription>
            </div>
            <Select value={String(cashFlowYear)} onValueChange={(value) => setCashFlowYear(Number(value))}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Ano" />
              </SelectTrigger>
              <SelectContent>
                {cashFlowYearOptions.map((year) => (
                  <SelectItem key={year} value={String(year)}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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
          <div className="flex flex-wrap items-center gap-3">
            <Select value={categoryMode} onValueChange={setCategoryMode}>
              <SelectTrigger className="w-[170px]">
                <SelectValue placeholder="Modo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="range">Ultimos meses</SelectItem>
                <SelectItem value="year">Ano especifico</SelectItem>
              </SelectContent>
            </Select>

            {categoryMode === 'range' ? (
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
            ) : (
              <Select value={String(categoryYear)} onValueChange={(value) => setCategoryYear(Number(value))}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Ano" />
                </SelectTrigger>
                <SelectContent>
                  {categoryYearOptions.map((yearOption) => (
                    <SelectItem key={yearOption} value={String(yearOption)}>
                      {yearOption}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={categoryTab} onValueChange={setCategoryTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="despesa">Despesas</TabsTrigger>
              <TabsTrigger value="receita">Receitas</TabsTrigger>
            </TabsList>
            <TabsContent value="despesa">
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
                      </PieChart>
                    </ResponsiveContainer>
                    <CategoryLegend data={expenseData} />
                  </div>
                  <div className="flex-1">
                    <CategoryList data={expenseData} total={expenseTotal} />
                  </div>
                </div>
              </SectionState>
            </TabsContent>
            <TabsContent value="receita">
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
                      </PieChart>
                    </ResponsiveContainer>
                    <CategoryLegend data={incomeData} />
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
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <Select value={String(budgetYear)} onValueChange={(value) => setBudgetYear(Number(value))}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Ano" />
              </SelectTrigger>
              <SelectContent>
                {budgetYearOptions.map((yearOption) => (
                  <SelectItem key={yearOption} value={String(yearOption)}>
                    {yearOption}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={String(budgetMonth)} onValueChange={(value) => setBudgetMonth(Number(value))}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Mes" />
              </SelectTrigger>
              <SelectContent>
                {budgetMonthOptions.map((option) => (
                  <SelectItem key={option.value} value={String(option.value)}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
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
