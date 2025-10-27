import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import LoadingSpinner from '@/components/ui/loading-spinner'
import { useApi } from '@/contexts/ApiContext'
import { formatCurrency } from '@/lib/formatters'
import { Plus, Edit2, Trash2, RefreshCcw } from 'lucide-react'

const categoryTypeOptions = [
  { value: 'income', label: 'Receita' },
  { value: 'expense', label: 'Despesa' },
]

function CategoryForm({ initialData, categories, onSubmit, onCancel, loading }) {
  const [form, setForm] = useState(() => ({
    nome: initialData?.nome ?? '',
    tipo: initialData?.tipo ?? 'expense',
    parent_id: initialData?.parent_id ?? '',
    cor: initialData?.cor ?? '',
    descricao: initialData?.descricao ?? '',
    ativo: initialData?.ativo ?? true,
    incluir_relatorios: initialData?.incluir_relatorios ?? true,
  }))

  const handleChange = (field) => (event) => {
    const value = event?.target ? event.target.value : event
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleCheckbox = (field) => (checked) => {
    setForm((prev) => ({ ...prev, [field]: !!checked }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const payload = {
      ...form,
      parent_id: form.parent_id || null,
    }
    onSubmit(payload)
  }

  const availableParents = categories.filter((cat) => !initialData || cat.id !== initialData.id)

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="nome">Nome</Label>
        <Input id="nome" value={form.nome} onChange={handleChange('nome')} required />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Tipo</Label>
          <Select value={form.tipo} onValueChange={(value) => setForm((prev) => ({ ...prev, tipo: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Tipo da categoria" />
            </SelectTrigger>
            <SelectContent>
              {categoryTypeOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Categoria pai</Label>
          <Select
            value={form.parent_id || 'none'}
            onValueChange={(value) => setForm((prev) => ({ ...prev, parent_id: value === 'none' ? '' : value }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Nenhuma" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Nenhuma</SelectItem>
              {availableParents.map((cat) => (
                <SelectItem key={cat.id} value={cat.id}>
                  {cat.nome}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="cor">Cor (hex opcional)</Label>
        <Input id="cor" value={form.cor} onChange={handleChange('cor')} placeholder="#ef4444" />
      </div>

      <div className="space-y-2">
        <Label htmlFor="descricao">Descrição</Label>
        <Input id="descricao" value={form.descricao} onChange={handleChange('descricao')} />
      </div>

      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-2">
          <Checkbox checked={form.ativo} onCheckedChange={handleCheckbox('ativo')} />
          <span>Categoria ativa</span>
        </label>
        <label className="flex items-center gap-2">
          <Checkbox checked={form.incluir_relatorios} onCheckedChange={handleCheckbox('incluir_relatorios')} />
          <span>Incluir em relatórios</span>
        </label>
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

export default function CategoriesPage() {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [mode, setMode] = useState('create')
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [feedback, setFeedback] = useState('')

  const categoriesQuery = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get('/categories', { params: { limit: 500 } })
      return response.data.categories ?? []
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload) => api.post('/categories', payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['categories'])
      setFeedback('Categoria criada com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível criar a categoria.'
      setFeedback(message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => api.put(`/categories/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['categories'])
      setFeedback('Categoria atualizada com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível atualizar a categoria.'
      setFeedback(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/categories/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['categories'])
      setFeedback('Categoria excluída com sucesso.')
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível excluir a categoria.'
      setFeedback(message)
    },
  })

  const handleCreate = () => {
    setMode('create')
    setSelectedCategory(null)
    setDialogOpen(true)
  }

  const handleEdit = (category) => {
    setMode('edit')
    setSelectedCategory(category)
    setDialogOpen(true)
  }

  const handleDelete = (category) => {
    if (window.confirm(`Excluir a categoria "${category.nome}"? Subcategorias também serão removidas.`)) {
      deleteMutation.mutate(category.id)
    }
  }

  const handleSubmit = (payload) => {
    if (mode === 'create') {
      createMutation.mutate(payload)
    } else if (selectedCategory) {
      updateMutation.mutate({ id: selectedCategory.id, payload })
    }
  }

  const categories = categoriesQuery.data ?? []
  const isLoading = categoriesQuery.isLoading

  const resumo = useMemo(() => {
    const total = categories.length
    const receitas = categories.filter((cat) => cat.tipo === 'income').length
    const despesas = categories.filter((cat) => cat.tipo === 'expense').length
    return { total, receitas, despesas }
  }, [categories])

  const transformHierarchy = (items, parentId = null, level = 0) => {
    return items
      .filter((item) => (item.parent_id || null) === parentId)
      .flatMap((item) => [
        { ...item, level },
        ...transformHierarchy(items, item.id, level + 1),
      ])
  }

  const hierarchicalCategories = useMemo(() => transformHierarchy(categories), [categories])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Categorias</h1>
          <p className="text-muted-foreground">Organize suas receitas e despesas em categorias hierárquicas.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => queryClient.invalidateQueries(['categories'])}>
            <RefreshCcw className="h-4 w-4 mr-2" /> Atualizar
          </Button>
          <Button onClick={handleCreate}>
            <Plus className="h-4 w-4 mr-2" /> Nova categoria
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
            <CardTitle>Total de categorias</CardTitle>
            <CardDescription>Receitas e despesas</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resumo.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Categorias de receita</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{resumo.receitas}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Categorias de despesa</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{resumo.despesas}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Estrutura de categorias</CardTitle>
          <CardDescription>As categorias são exibidas na ordem hierárquica.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-10 flex justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : hierarchicalCategories.length === 0 ? (
            <p className="text-muted-foreground">Nenhuma categoria cadastrada.</p>
          ) : (
            <div className="space-y-2">
              {hierarchicalCategories.map((category) => (
                <div
                  key={category.id}
                  className="flex items-center justify-between border rounded-lg px-4 py-3"
                  style={{ marginLeft: `${category.level * 16}px` }}
                >
                  <div>
                    <div className="font-semibold flex items-center gap-2">
                      {category.nome}
                      {category.cor && (
                        <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: category.cor }} />
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {category.tipo === 'income' ? 'Receita' : 'Despesa'}
                      {category.descricao ? ` • ${category.descricao}` : ''}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(category)}>
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(category)}>
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{mode === 'create' ? 'Nova categoria' : 'Editar categoria'}</DialogTitle>
            <DialogDescription>
              {mode === 'create'
                ? 'Preencha os campos para criar uma nova categoria.'
                : 'Atualize as informações da categoria selecionada.'}
            </DialogDescription>
          </DialogHeader>
          <CategoryForm
            initialData={selectedCategory}
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
