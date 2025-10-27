import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { useApi } from '@/contexts/ApiContext'
import LoadingSpinner from '@/components/ui/loading-spinner'
import { formatCurrency } from '@/lib/formatters'
import { Plus, Trash2, Edit2, RefreshCcw } from 'lucide-react'

const accountTypeOptions = [
  { value: 'cash', label: 'Dinheiro' },
  { value: 'checking', label: 'Conta Corrente' },
  { value: 'savings', label: 'Poupança' },
  { value: 'credit', label: 'Cartão de Crédito' },
  { value: 'investment', label: 'Investimentos' },
  { value: 'other', label: 'Outros' },
]

function AccountForm({ onSubmit, onCancel, initialData, loading }) {
  const [formData, setFormData] = useState(() => ({
    nome: initialData?.nome ?? '',
    tipo: initialData?.tipo ?? 'checking',
    saldo_inicial: initialData?.saldo_inicial ?? '0',
    descricao: initialData?.descricao ?? '',
    moeda: initialData?.moeda ?? 'BRL',
    ativo: initialData?.ativo ?? true,
    incluir_relatorios: initialData?.incluir_relatorios ?? true,
  }))

  const handleChange = (field) => (event) => {
    const value = event?.target ? event.target.value : event
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleCheckbox = (field) => (checked) => {
    setFormData((prev) => ({ ...prev, [field]: !!checked }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const payload = {
      ...formData,
      saldo_inicial: Number(formData.saldo_inicial ?? 0),
    }
    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="nome">Nome</Label>
        <Input
          id="nome"
          value={formData.nome}
          onChange={handleChange('nome')}
          placeholder="Ex: Conta Corrente"
          required
        />
      </div>

      <div className="space-y-2">
        <Label>Tipo</Label>
        <Select value={formData.tipo} onValueChange={(value) => setFormData((prev) => ({ ...prev, tipo: value }))}>
          <SelectTrigger>
            <SelectValue placeholder="Selecione o tipo" />
          </SelectTrigger>
          <SelectContent>
            {accountTypeOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="saldo_inicial">Saldo inicial</Label>
          <Input
            id="saldo_inicial"
            type="number"
            step="0.01"
            value={formData.saldo_inicial}
            onChange={handleChange('saldo_inicial')}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="moeda">Moeda</Label>
          <Input
            id="moeda"
            value={formData.moeda}
            onChange={handleChange('moeda')}
            maxLength={3}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="descricao">Descrição</Label>
        <Input
          id="descricao"
          value={formData.descricao}
          onChange={handleChange('descricao')}
          placeholder="Detalhes opcionais"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-2">
          <Checkbox checked={formData.ativo} onCheckedChange={handleCheckbox('ativo')} />
          <span>Conta ativa</span>
        </label>
        <label className="flex items-center gap-2">
          <Checkbox
            checked={formData.incluir_relatorios}
            onCheckedChange={handleCheckbox('incluir_relatorios')}
          />
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

export default function AccountsPage() {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [mode, setMode] = useState('create') // create | edit
  const [feedback, setFeedback] = useState('')

  const accountsQuery = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const response = await api.get('/accounts', { params: { limit: 500, skip: 0 } })
      return response.data.accounts ?? []
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload) => api.post('/accounts', payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['accounts'])
      setFeedback('Conta criada com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível criar a conta.'
      setFeedback(message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => api.put(`/accounts/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['accounts'])
      setFeedback('Conta atualizada com sucesso.')
      setDialogOpen(false)
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível atualizar a conta.'
      setFeedback(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/accounts/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['accounts'])
      setFeedback('Conta removida com sucesso.')
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Não foi possível remover a conta.'
      setFeedback(message)
    },
  })

  const handleCreate = () => {
    setMode('create')
    setSelectedAccount(null)
    setDialogOpen(true)
  }

  const handleEdit = (account) => {
    setMode('edit')
    setSelectedAccount(account)
    setDialogOpen(true)
  }

  const handleDelete = (account) => {
    if (window.confirm(`Tem certeza que deseja excluir a conta "${account.nome}"?`)) {
      deleteMutation.mutate(account.id)
    }
  }

  const handleSubmit = (payload) => {
    if (mode === 'create') {
      createMutation.mutate(payload)
    } else if (selectedAccount) {
      updateMutation.mutate({ id: selectedAccount.id, payload })
    }
  }

  const isLoading = accountsQuery.isLoading
  const accounts = accountsQuery.data ?? []

  const resumo = useMemo(() => {
    const patrim = accounts.filter((acc) => acc.tipo !== 'credit').reduce((sum, acc) => sum + Number(acc.saldo_inicial ?? 0), 0)
    const dividas = accounts.filter((acc) => acc.tipo === 'credit' && Number(acc.saldo_inicial ?? 0) < 0).reduce((sum, acc) => sum + Math.abs(Number(acc.saldo_inicial ?? 0)), 0)
    return { patri: patrim, dividas, liquido: patrim - dividas }
  }, [accounts])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contas</h1>
          <p className="text-muted-foreground">Gerencie suas contas bancárias, cartões e investimentos</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => queryClient.invalidateQueries(['accounts'])}>
            <RefreshCcw className="h-4 w-4 mr-2" /> Atualizar
          </Button>
          <Button onClick={handleCreate}>
            <Plus className="h-4 w-4 mr-2" /> Nova Conta
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
            <CardTitle>Patrimônio Total</CardTitle>
            <CardDescription>Soma das contas não creditícias</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(resumo.patri)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Dívidas em cartões</CardTitle>
            <CardDescription>Saldo negativo em cartões de crédito</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{formatCurrency(resumo.dividas)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Patrimônio Líquido</CardTitle>
            <CardDescription>Patrimônio menos dívidas</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{formatCurrency(resumo.liquido)}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suas contas</CardTitle>
          <CardDescription>Contas armazenadas no banco de dados</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-10 flex justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : accounts.length === 0 ? (
            <p className="text-muted-foreground">Nenhuma conta cadastrada ainda.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left border-b">
                    <th className="py-2">Nome</th>
                    <th className="py-2">Tipo</th>
                    <th className="py-2">Saldo inicial</th>
                    <th className="py-2">Moeda</th>
                    <th className="py-2">Ativa</th>
                    <th className="py-2 w-32 text-right">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.map((account) => (
                    <tr key={account.id} className="border-b last:border-transparent">
                      <td className="py-2">{account.nome}</td>
                      <td className="py-2 capitalize">{account.tipo}</td>
                      <td className="py-2">{formatCurrency(account.saldo_atual ?? account.saldo_inicial ?? 0)}</td>
                      <td className="py-2">{account.moeda}</td>
                      <td className="py-2">{account.ativo ? 'Sim' : 'Não'}</td>
                      <td className="py-2 text-right space-x-2">
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(account)}>
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(account)}>
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{mode === 'create' ? 'Nova conta' : 'Editar conta'}</DialogTitle>
            <DialogDescription>
              Preencha os campos abaixo para {mode === 'create' ? 'cadastrar uma nova conta.' : 'atualizar a conta selecionada.'}
            </DialogDescription>
          </DialogHeader>
          <AccountForm
            initialData={selectedAccount}
            onSubmit={handleSubmit}
            onCancel={() => setDialogOpen(false)}
            loading={createMutation.isLoading || updateMutation.isLoading}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
