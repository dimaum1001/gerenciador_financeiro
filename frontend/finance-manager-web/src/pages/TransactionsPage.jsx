import { useMemo, useState } from 'react'
import { eachMonthOfInterval, endOfMonth, format, startOfMonth, subMonths } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { useApi } from '@/contexts/ApiContext'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover'
import { Command, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem } from '@/components/ui/command'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import LoadingSpinner from '@/components/ui/loading-spinner'
import { formatCurrency } from '@/lib/formatters'
import {
  transactionTypeOptions,
  transactionStatusOptions,
  paymentMethodOptions,
  normalizeTransactionType,
  normalizeTransactionStatus,
  normalizePaymentMethod,
  getField,
} from '@/lib/api-locale'
import { cn } from '@/lib/utils'
import { Plus, Edit2, Trash2, RefreshCcw, ChevronsUpDown, Check } from 'lucide-react'

const typeFilterOptions = [
  { value: 'all', label: 'Todos os tipos' },
  { value: 'receita', label: 'Receitas' },
  { value: 'despesa', label: 'Despesas' },
]

const transactionTypeLabels = Object.fromEntries(transactionTypeOptions.map((option) => [option.value, option.label]))
const statusLabelMap = Object.fromEntries(transactionStatusOptions.map((option) => [option.value, option.label]))

function AutocompleteSelect({
  options = [],
  value,
  onChange,
  placeholder = 'Selecione...',
  searchPlaceholder = 'Digite para buscar...',
  emptyMessage = 'Nenhum resultado encontrado.',
  disabled = false,
  className,
}) {
  const [open, setOpen] = useState(false)
  const selectedOption = options.find((option) => option.value === value)

  const handleSelect = (selectedValue) => {
    onChange?.(selectedValue)
    setOpen(false)
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn('w-full justify-between', className)}
          disabled={disabled}
        >
          {selectedOption ? selectedOption.label : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="start"
        className="w-[var(--radix-popover-trigger-width)] min-w-[220px] p-0"
      >
        <Command loop>
          <CommandInput placeholder={searchPlaceholder} autoFocus />
          <CommandEmpty>{emptyMessage}</CommandEmpty>
          <CommandList>
            <CommandGroup>
              {options.map((option, index) => (
                <CommandItem
                  key={`${option.value ?? 'empty'}-${index}`}
                  value={`${option.value ?? ''} ${option.label}`}
                  onSelect={() => handleSelect(option.value)}
                >
                  <Check
                    className={cn(
                      'mr-2 h-4 w-4',
                      option.value === value ? 'opacity-100' : 'opacity-0'
                    )}
                  />
                  <div>
                    <p>{option.label}</p>
                    {option.description && (
                      <p className="text-xs text-muted-foreground">{option.description}</p>
                    )}
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

function TransactionForm({ initialData, accounts, categories, onSubmit, onCancel, loading }) {
  const [form, setForm] = useState(() => ({
    descricao: initialData?.descricao ?? '',
    valor: initialData?.valor != null ? Number(initialData.valor).toString() : '',
    moeda: initialData?.moeda ?? 'BRL',
    tipo: normalizeTransactionType(initialData?.tipo_portugues ?? initialData?.tipo ?? 'despesa'),
    data_lancamento: initialData?.data_lancamento ?? new Date().toISOString().split('T')[0],
    conta_id: getField(initialData, 'conta_id', 'account_id') ?? (accounts[0]?.id ?? ''),
    categoria_id: getField(initialData, 'categoria_id', 'category_id') ?? '',
    status: normalizeTransactionStatus(initialData?.status) ?? 'pendente',
    metodo_pagamento: normalizePaymentMethod(getField(initialData, 'metodo_pagamento', 'payment_method')) ?? '',
    tags: initialData?.tags?.join(', ') ?? '',
  }))

  const handleChange = (field) => (event) => {
    const value = event?.target ? event.target.value : event
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const payload = {
      ...form,
      valor: Number(form.valor ?? 0),
      tags: form.tags ? form.tags.split(',').map((tag) => tag.trim()).filter(Boolean) : [],
      categoria_id: form.categoria_id || null,
      metodo_pagamento: form.metodo_pagamento || null,
      status: normalizeTransactionStatus(form.status ?? 'pendente'),
    }
    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="descricao">Descricao</Label>
        <Input id="descricao" value={form.descricao} onChange={handleChange('descricao')} required />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Conta</Label>
          <AutocompleteSelect
            options={accounts.map((account) => ({ value: account.id, label: account.nome }))}
            value={form.conta_id}
            onChange={(value) => setForm((prev) => ({ ...prev, conta_id: value }))}
            placeholder="Selecione a conta"
            searchPlaceholder="Busque pela conta..."
            disabled={!accounts.length}
          />
        </div>

        <div className="space-y-2">
          <Label>Categoria</Label>
          <AutocompleteSelect
            options={[
              { value: '', label: 'Sem categoria' },
              ...categories.map((category) => ({ value: category.id, label: category.nome })),
            ]}
            value={form.categoria_id || ''}
            onChange={(value) => setForm((prev) => ({ ...prev, categoria_id: value || '' }))}
            placeholder="Opcional"
            searchPlaceholder="Busque pela categoria..."
          />
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label>Tipo</Label>
          <AutocompleteSelect
            options={transactionTypeOptions}
            value={form.tipo}
            onChange={(value) => setForm((prev) => ({ ...prev, tipo: value }))}
            placeholder="Tipo"
            searchPlaceholder="Busque pelo tipo..."
          />
        </div>

        <div className="space-y-2">
          <Label>Status</Label>
          <AutocompleteSelect
            options={transactionStatusOptions}
            value={form.status}
            onChange={(value) => setForm((prev) => ({ ...prev, status: value }))}
            placeholder="Status"
            searchPlaceholder="Busque pelo status..."
          />
        </div>

        <div className="space-y-2">
          <Label>Data</Label>
          <Input id="data_lancamento" type="date" value={form.data_lancamento} onChange={handleChange('data_lancamento')} required />
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="valor">Valor</Label>
          <Input id="valor" type="number" step="0.01" value={form.valor} onChange={handleChange('valor')} required />
        </div>
        <div className="space-y-2">
          <Label>Metodo de pagamento</Label>
        <AutocompleteSelect
          options={[
            { value: '', label: 'Nao informar' },
            ...paymentMethodOptions,
          ]}
          value={form.metodo_pagamento || ''}
          onChange={(value) => setForm((prev) => ({ ...prev, metodo_pagamento: value }))}
          placeholder="Opcional"
          searchPlaceholder="Busque pelo metodo..."
        />
        </div>
        <div className="space-y-2">
          <Label htmlFor="tags">Tags (separadas por virgula)</Label>
          <Input id="tags" value={form.tags} onChange={handleChange('tags')} />
        </div>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Salvando...' : 'Salvar'}
        </Button>
      </DialogFooter>
    </form>
  )
}

export default function TransactionsPage() {
  const { api } = useApi()
  const queryClient = useQueryClient()

  const [selectedPeriod, setSelectedPeriod] = useState(() => format(new Date(), 'yyyy-MM'))
  const [typeFilter, setTypeFilter] = useState('all')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [mode, setMode] = useState('create')
  const [selectedTransaction, setSelectedTransaction] = useState(null)
  const [feedback, setFeedback] = useState('')

  const availableMonths = useMemo(() => {
    const end = startOfMonth(new Date())
    const start = subMonths(end, 59)
    return eachMonthOfInterval({ start, end }).reverse().map((date) => ({
      value: format(date, 'yyyy-MM'),
      year: format(date, 'yyyy'),
      label: format(date, "MMMM 'de' yyyy", { locale: ptBR }),
    }))
  }, [])

  const yearOptions = useMemo(() => {
    const years = new Set(availableMonths.map((option) => option.year))
    return Array.from(years).sort((a, b) => Number(b) - Number(a))
  }, [availableMonths])

  const selectedYear = useMemo(() => selectedPeriod.split('-')[0], [selectedPeriod])

  const monthOptions = useMemo(
    () =>
      availableMonths
        .filter((option) => option.year === selectedYear)
        .map((option) => ({
          value: option.value,
          label: option.label.charAt(0).toUpperCase() + option.label.slice(1),
        })),
    [availableMonths, selectedYear],
  )

  const { startDateIso, endDateIso, selectedMonthLabel } = useMemo(() => {
    const [yearStr, monthStr] = selectedPeriod.split('-')
    const year = Number(yearStr)
    const month = Number(monthStr)
    const start = startOfMonth(new Date(year, month - 1))
    const end = endOfMonth(start)
    const label = format(start, "MMMM 'de' yyyy", { locale: ptBR })
    return {
      startDateIso: format(start, 'yyyy-MM-dd'),
      endDateIso: format(end, 'yyyy-MM-dd'),
      selectedMonthLabel: label.charAt(0).toUpperCase() + label.slice(1),
    }
  }, [selectedPeriod])

  const accountsQuery = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const response = await api.get('/accounts', { params: { limit: 500 } })
      return response.data.accounts ?? []
    },
  })

  const categoriesQuery = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get('/categories', { params: { limit: 500 } })
      return response.data.categories ?? []
    },
  })

  const transactionsQuery = useQuery({
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

  const createMutation = useMutation({
    mutationFn: (payload) => api.post('/transactions', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      setFeedback('Transacao criada com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Nao foi possivel criar a transacao.'
      setFeedback(message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => api.put(`/transactions/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      setFeedback('Transacao atualizada com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Nao foi possivel atualizar a transacao.'
      setFeedback(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/transactions/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      setFeedback('Transacao excluida.')
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Nao foi possivel excluir a transacao.'
      setFeedback(message)
    },
  })

  const handleCreate = () => {
    setMode('create')
    setSelectedTransaction(null)
    setDialogOpen(true)
  }

  const handleEdit = (transaction) => {
    setMode('edit')
    setSelectedTransaction(transaction)
    setDialogOpen(true)
  }

  const handleDelete = (transaction) => {
    if (window.confirm('Deseja realmente excluir esta transacao?')) {
      deleteMutation.mutate(transaction.id)
    }
  }

  const handleSubmit = (payload) => {
    if (mode === 'create') {
      createMutation.mutate(payload)
    } else if (selectedTransaction) {
      updateMutation.mutate({ id: selectedTransaction.id, payload })
    }
  }

  const transactions = transactionsQuery.data ?? []
  const accounts = accountsQuery.data ?? []
  const categories = categoriesQuery.data ?? []

  const getTransactionContaId = (tx) => getField(tx, 'conta_id', 'account_id')
  const getTransactionCategoriaId = (tx) => getField(tx, 'categoria_id', 'category_id')
  const getTransactionTipo = (tx) => normalizeTransactionType(tx?.tipo_portugues ?? tx?.tipo)
  const getTransactionStatus = (tx) => normalizeTransactionStatus(tx?.status_portugues ?? tx?.status)
  const getTransactionMetodo = (tx) => normalizePaymentMethod(tx?.metodo_pagamento ?? tx?.payment_method)

  const accountsMap = useMemo(() => Object.fromEntries(accounts.map((account) => [account.id, account.nome])), [accounts])
  const categoriesMap = useMemo(() => Object.fromEntries(categories.map((category) => [category.id, category.nome])), [categories])

  const sortedTransactions = useMemo(() => {
    return [...transactions].sort((a, b) => new Date(b.data_lancamento) - new Date(a.data_lancamento))
  }, [transactions])

  const filteredTransactions = useMemo(() => {
    if (typeFilter === 'all') {
      return transactions
    }
    return transactions.filter((tx) => getTransactionTipo(tx) === typeFilter)
  }, [transactions, typeFilter])

  const filterLabel = useMemo(() => {
    return typeFilterOptions.find((option) => option.value === typeFilter)?.label ?? ''
  }, [typeFilter])

  const isLoading =
    transactionsQuery.isLoading ||
    transactionsQuery.isFetching ||
    accountsQuery.isLoading ||
    categoriesQuery.isLoading

  const resumo = useMemo(() => {
    const receitas = filteredTransactions
      .filter((tx) => getTransactionTipo(tx) === 'receita')
      .reduce((sum, tx) => sum + Number(tx.valor || 0), 0)
    const despesas = filteredTransactions
      .filter((tx) => getTransactionTipo(tx) === 'despesa')
      .reduce((sum, tx) => sum + Number(tx.valor || 0), 0)
    return {
      receitas,
      despesas,
      saldo: receitas - despesas,
    }
  }, [filteredTransactions])

  const statusResumo = useMemo(() => {
    const base = Object.fromEntries(transactionStatusOptions.map((option) => [option.value, 0]))
    filteredTransactions.forEach((tx) => {
      const status = getTransactionStatus(tx)
      if (status) {
        base[status] = (base[status] ?? 0) + 1
      }
    })
    return base
  }, [filteredTransactions])

  const dailyBreakdown = useMemo(() => {
    if (!filteredTransactions.length) {
      return []
    }

    const byDay = new Map()
    filteredTransactions.forEach((tx) => {
      const currentDate = new Date(tx.data_lancamento)
      const label = format(currentDate, 'dd/MM', { locale: ptBR })
      const entry = byDay.get(label) ?? { date: currentDate, income: 0, expense: 0, total: 0 }

      entry.total += 1
      const value = Number(tx.valor || 0)
      const tipo = getTransactionTipo(tx)
      if (tipo === 'receita') {
        entry.income += value
      }
      if (tipo === 'despesa') {
        entry.expense += value
      }

      byDay.set(label, entry)
    })

    return Array.from(byDay.entries())
      .map(([label, data]) => ({
        label,
        income: data.income,
        expense: data.expense,
        total: data.total,
        balance: data.income - data.expense,
        sortValue: data.date.getTime(),
      }))
      .sort((a, b) => a.sortValue - b.sortValue)
  }, [filteredTransactions])

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Transacoes</h1>
          <p className="text-muted-foreground">Cadastre e acompanhe suas receitas, despesas e transferencias.</p>
          <p className="text-sm text-muted-foreground">{typeFilter === 'all' ? 'Exibindo receitas e despesas.' : `Exibindo apenas ${filterLabel}.`}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 md:justify-end">
          <AutocompleteSelect
            className="w-[160px]"
            options={yearOptions.map((year) => ({ value: year, label: year }))}
            value={selectedYear}
            onChange={(year) => {
              if (!year || year === selectedYear) return
              const [, currentMonth] = selectedPeriod.split('-')
              const sameMonth = availableMonths.find((option) => option.value === `${year}-${currentMonth}`)
              const fallback = availableMonths.find((option) => option.year === year)
              if (sameMonth) {
                setSelectedPeriod(sameMonth.value)
              } else if (fallback) {
                setSelectedPeriod(fallback.value)
              }
            }}
            placeholder="Selecione o ano"
            searchPlaceholder="Buscar ano..."
          />
          <AutocompleteSelect
            className="w-[220px]"
            options={monthOptions}
            value={selectedPeriod}
            onChange={setSelectedPeriod}
            placeholder="Selecione o mes"
            searchPlaceholder="Buscar mes..."
            emptyMessage="Nenhum mes disponivel."
          />
          <AutocompleteSelect
            className="w-[220px]"
            options={typeFilterOptions}
            value={typeFilter}
            onChange={setTypeFilter}
            placeholder="Filtrar por tipo"
            searchPlaceholder="Digite para filtrar..."
          />
          <Button variant="outline" onClick={() => queryClient.invalidateQueries({ queryKey: ['transactions'] })}>
            <RefreshCcw className="h-4 w-4 mr-2" /> Atualizar
          </Button>
          <Button onClick={handleCreate} disabled={!accounts.length}>
            <Plus className="h-4 w-4 mr-2" />
            {accounts.length ? 'Nova transacao' : 'Cadastre uma conta primeiro'}
          </Button>
        </div>
      </div>

      {feedback && (
        <Alert>
          <AlertDescription>{feedback}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total de receitas</CardTitle>
            <CardDescription>{`Somatorio das transacoes de entrada em ${selectedMonthLabel}`}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(resumo.receitas)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Total de despesas</CardTitle>
            <CardDescription>{`Somatorio das transacoes de saida em ${selectedMonthLabel}`}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{formatCurrency(resumo.despesas)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{`Saldo do periodo (${selectedMonthLabel})`}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{formatCurrency(resumo.saldo)}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Status das transacoes</CardTitle>
          <CardDescription>{`Quantidade de registros em ${selectedMonthLabel}`}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-6">
          {transactionStatusOptions.map((option) => (
            <div key={option.value} className="space-y-1">
              <p className="text-sm text-muted-foreground">{option.label}</p>
              <p className="text-lg font-semibold">{statusResumo[option.value] ?? 0}</p>
            </div>
          ))}
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Total</p>
            <p className="text-lg font-semibold">{filteredTransactions.length}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Movimentacao diaria</CardTitle>
          <CardDescription>{`Resumo rapido das transacoes de ${selectedMonthLabel}`}</CardDescription>
        </CardHeader>
        <CardContent>
          {dailyBreakdown.length === 0 ? (
            <p className="text-sm text-muted-foreground">Nao ha transacoes registradas para o mes selecionado.</p>
          ) : (
            <div className="space-y-3">
              {dailyBreakdown.map((day) => (
                <div key={day.label} className="flex items-center justify-between text-sm">
                  <div>
                    <p className="font-medium">{day.label}</p>
                    <p className="text-muted-foreground">{`${day.total} transacoes`}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-green-600">{formatCurrency(day.income)}</p>
                    <p className="text-red-600">-{formatCurrency(day.expense)}</p>
                    <p className="font-semibold">{formatCurrency(day.balance)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Todas as transacoes registradas</CardTitle>
          <CardDescription>Listagem completa de todas as transacoes (independente dos filtros).</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-10 flex justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : sortedTransactions.length === 0 ? (
            <p className="text-muted-foreground">Nenhuma transacao cadastrada.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left border-b">
                    <th className="py-2">Data</th>
                    <th className="py-2">Descricao</th>
                    <th className="py-2">Conta</th>
                    <th className="py-2">Categoria</th>
                    <th className="py-2">Tipo</th>
                    <th className="py-2">Valor</th>
                    <th className="py-2">Status</th>
                    <th className="py-2 w-32 text-right">Acoes</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedTransactions.map((transaction) => {
                    const valorNumerico = Number(transaction.valor || 0)
                    const tipoNormalizado = getTransactionTipo(transaction)
                    const statusNormalizado = getTransactionStatus(transaction)
                    const valorFormatado = tipoNormalizado === 'despesa' ? formatCurrency(valorNumerico * -1) : formatCurrency(valorNumerico)
                    const contaId = getTransactionContaId(transaction)
                    const categoriaId = getTransactionCategoriaId(transaction)
                    return (
                      <tr key={transaction.id} className="border-b last:border-transparent">
                        <td className="py-2">{format(new Date(transaction.data_lancamento), 'dd/MM/yyyy')}</td>
                        <td className="py-2">{transaction.descricao}</td>
                        <td className="py-2">{accountsMap[contaId] ?? '--'}</td>
                        <td className="py-2">{categoriaId ? categoriesMap[categoriaId] ?? '--' : '--'}</td>
                        <td className="py-2">{transactionTypeLabels[tipoNormalizado] ?? tipoNormalizado}</td>
                        <td className="py-2">{valorFormatado}</td>
                        <td className="py-2">{statusLabelMap[statusNormalizado] ?? statusNormalizado}</td>
                        <td className="py-2 text-right space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => handleEdit(transaction)}>
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(transaction)}>
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>{mode === 'create' ? 'Nova transacao' : 'Editar transacao'}</DialogTitle>
            <DialogDescription>Informe os dados da transacao financeira.</DialogDescription>
          </DialogHeader>
          <TransactionForm
            initialData={selectedTransaction}
            accounts={accounts}
            categories={categories}
            onSubmit={handleSubmit}
            onCancel={() => setDialogOpen(false)}
            loading={createMutation.isLoading || updateMutation.isLoading}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
