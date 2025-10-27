import { useMemo, useState } from 'react'
import { useApi } from '@/contexts/ApiContext'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import LoadingSpinner from '@/components/ui/loading-spinner'
import { formatCurrency } from '@/lib/formatters'
import { Plus, Edit2, Trash2, RefreshCcw } from 'lucide-react'

const monthOptions = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

function BudgetForm({ categories, initialData, onSubmit, onCancel, loading }) {
  const [form, setForm] = useState(() => ({
    category_id: initialData?.category_id ?? (categories[0]?.id ?? ''),
    ano: initialData?.ano ?? new Date().getFullYear(),
    mes: initialData?.mes ?? new Date().getMonth() + 1,
    valor_planejado: initialData?.valor_planejado != null ? Number(initialData.valor_planejado).toString() : '0',
    descricao: initialData?.descricao ?? '',
    incluir_subcategorias: initialData?.incluir_subcategorias ?? true,
    alerta_percentual: initialData?.alerta_percentual ?? 80,
  }))

  const handleChange = (field) => (event) => {
    const value = event?.target ? event.target.value : event
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const payload = {
      ...form,
      valor_planejado: Number(form.valor_planejado ?? 0),
      ano: Number(form.ano),
      mes: Number(form.mes),
      alerta_percentual: Number(form.alerta_percentual),
      incluir_subcategorias: Boolean(form.incluir_subcategorias),
    }
    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label>Categoria</Label>
        <Select value={form.category_id} onValueChange={(value) => setForm((prev) => ({ ...prev, category_id: value }))}>
          <SelectTrigger>
            <SelectValue placeholder="Selecione a categoria" />
          </SelectTrigger>
          <SelectContent>
            {categories.map((category) => (
              <SelectItem key={category.id} value={category.id}>
                {category.nome}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Ano</Label>
          <Input type="number" value={form.ano} onChange={handleChange('ano')} required />
        </div>
        <div className="space-y-2">
          <Label>Mês</Label>
          <Select value={form.mes.toString()} onValueChange={(value) => setForm((prev) => ({ ...prev, mes: Number(value) }))}>
            <SelectTrigger>
              <SelectValue placeholder="Mês" />
            </SelectTrigger>
            <SelectContent>
              {monthOptions.map((label, index) => (
                <SelectItem key={label} value={(index + 1).toString()}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="valor_planejado">Valor planejado</Label>
          <Input
            id="valor_planejado"
            type="number"
            step="0.01"
            value={form.valor_planejado}
            onChange={handleChange('valor_planejado')}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="alerta_percentual">Alerta (%)</Label>
          <Input
            id="alerta_percentual"
            type="number"
            min={0}
            max={100}
            value={form.alerta_percentual}
            onChange={handleChange('alerta_percentual')}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="descricao">Descrição</Label>
        <Input id="descricao" value={form.descricao} onChange={handleChange('descricao')} />
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

export default function BudgetsPage() {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [mode, setMode] = useState('create')
  const [selectedBudget, setSelectedBudget] = useState(null)
  const [feedback, setFeedback] = useState('')

  const categoriesQuery = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get('/categories', { params: { limit: 500 } })
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

  const createMutation = useMutation({
    mutationFn: (payload) => api.post('/budgets', payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['budgets'])
      setFeedback('Orçamento criado com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível criar o orçamento.'
      setFeedback(message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => api.put(`/budgets/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['budgets'])
      setFeedback('Orçamento atualizado com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível atualizar o orçamento.'
      setFeedback(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/budgets/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['budgets'])
      setFeedback('Orçamento removido.')
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível remover o orçamento.'
      setFeedback(message)
    },
  })

  const handleCreate = () => {
    setMode('create')
    setSelectedBudget(null)
    setDialogOpen(true)
  }

  const handleEdit = (budget) => {
    setMode('edit')
    setSelectedBudget(budget)
    setDialogOpen(true)
  }

  const handleDelete = (budget) => {
    if (window.confirm('Excluir este orçamento?')) {
      deleteMutation.mutate(budget.id)
    }
  }

  const handleSubmit = (payload) => {
    if (mode === 'create') {
      createMutation.mutate(payload)
    } else if (selectedBudget) {
      updateMutation.mutate({ id: selectedBudget.id, payload })
    }
  }

  const budgets = budgetsQuery.data ?? []
  const categories = categoriesQuery.data ?? []
  const isLoading = budgetsQuery.isLoading || categoriesQuery.isLoading

  const resumo = useMemo(() => {
    const planejado = budgets.reduce((sum, budget) => sum + Number(budget.valor_planejado || 0), 0)
    const realizado = budgets.reduce((sum, budget) => sum + Number(budget.valor_realizado || 0), 0)
    return {
      planejado,
      realizado,
      restante: planejado - realizado,
    }
  }, [budgets])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Orçamentos</h1>
          <p className="text-muted-foreground">Defina metas financeiras para cada categoria.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => queryClient.invalidateQueries(['budgets'])}>
            <RefreshCcw className="h-4 w-4 mr-2" /> Atualizar
          </Button>
          <Button onClick={handleCreate} disabled={!categories.length}>
            <Plus className="h-4 w-4 mr-2" />
            {categories.length ? 'Novo orçamento' : 'Cadastre uma categoria primeiro'}
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
            <CardTitle>Total planejado</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{formatCurrency(resumo.planejado)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Total realizado</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(resumo.realizado)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Valor restante</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{formatCurrency(resumo.restante)}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Orçamentos cadastrados</CardTitle>
          <CardDescription>Controle de metas por categoria.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-10 flex justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : budgets.length === 0 ? (
            <p className="text-muted-foreground">Nenhum orçamento cadastrado.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left border-b">
                    <th className="py-2">Categoria</th>
                    <th className="py-2">Período</th>
                    <th className="py-2">Planejado</th>
                    <th className="py-2">Realizado</th>
                    <th className="py-2">Restante</th>
                    <th className="py-2 w-32 text-right">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {budgets.map((budget) => {
                    const categoria = categories.find((cat) => cat.id === budget.category_id)
                    const restante = Number(budget.valor_planejado || 0) - Number(budget.valor_realizado || 0)
                    return (
                      <tr key={budget.id} className="border-b last:border-transparent">
                        <td className="py-2">{categoria?.nome || '—'}</td>
                        <td className="py-2">{String(budget.mes).padStart(2, '0')}/{budget.ano}</td>
                        <td className="py-2">{formatCurrency(budget.valor_planejado)}</td>
                        <td className="py-2">{formatCurrency(budget.valor_realizado)}</td>
                        <td className="py-2">{formatCurrency(restante)}</td>
                        <td className="py-2 text-right space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => handleEdit(budget)}>
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(budget)}>
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
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{mode === 'create' ? 'Novo orçamento' : 'Editar orçamento'}</DialogTitle>
            <DialogDescription>Defina o valor planejado para a categoria selecionada.</DialogDescription>
          </DialogHeader>
          <BudgetForm
            categories={categories}
            initialData={selectedBudget}
            onSubmit={handleSubmit}
            onCancel={() => setDialogOpen(false)}
            loading={createMutation.isLoading || updateMutation.isLoading}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
