import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Globe, 
  Download,
  Upload,
  Trash2,
  Save,
  Eye,
  EyeOff,
  Loader2
} from 'lucide-react'
import { formatCurrency } from '@/lib/formatters'
import { useApi } from '@/contexts/ApiContext'
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/components/theme-provider'

export default function SettingsPage() {
  const { user } = useAuth()
  const { theme, setTheme } = useTheme()
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [showPassword, setShowPassword] = useState(false)
  const [importAccount, setImportAccount] = useState('')
  const [importFile, setImportFile] = useState(null)
  const [importDryRun, setImportDryRun] = useState(true)
  const [importResult, setImportResult] = useState(null)
  const [importError, setImportError] = useState('')
  const [importLoading, setImportLoading] = useState(false)
  const [lastImportDryRun, setLastImportDryRun] = useState(true)
  
  // Estados para as configurações
  const [profile, setProfile] = useState({
    nome: user?.nome || '',
    email: user?.email || '',
    telefone: user?.telefone || '',
    timezone: 'America/Sao_Paulo',
    moeda: 'BRL',
    formato_data: 'DD/MM/YYYY'
  })

  const [notifications, setNotifications] = useState({
    email_transacoes: true,
    email_orcamentos: true,
    email_vencimentos: true,
    push_transacoes: false,
    push_orcamentos: true,
    push_vencimentos: true
  })

  const [security, setSecurity] = useState({
    senha_atual: '',
    senha_nova: '',
    confirmar_senha: '',
    two_factor: false,
    login_notifications: true
  })

  const accountsQuery = useQuery({
    queryKey: ['accounts', 'import'],
    queryFn: async () => {
      const response = await api.get('/accounts', { params: { limit: 500, skip: 0 } })
      return response.data.accounts ?? []
    }
  })

  const accounts = accountsQuery.data ?? []
  const hasAccounts = accounts.length > 0

  const normalizeErrorDetail = (detail) => {
    if (!detail) return ''
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (!item) return null
          if (typeof item === 'string') return item
          const message = item.msg || item.message || item.detail
          const loc = Array.isArray(item.loc) ? item.loc.join(' > ') : item.loc
          if (message && loc) return `${message} (${loc})`
          if (message) return message
          try {
            return JSON.stringify(item)
          } catch {
            return null
          }
        })
        .filter(Boolean)
        .join(' | ')
    }
    if (typeof detail === 'object') {
      const message = detail.msg || detail.message || detail.detail
      if (message) return message
      try {
        return JSON.stringify(detail)
      } catch {
        return ''
      }
    }
    return String(detail)
  }

  const buildImportErrorMessage = (error) => {
    const fallback = 'Não foi possível importar o arquivo.'
    if (!error) return fallback
    const detail = error.response?.data?.detail ?? error.message ?? error
    const normalized = normalizeErrorDetail(detail)
    return normalized || fallback
  }

  const handleImportFileChange = (event) => {
    const file = event.target.files?.[0]
    setImportFile(file || null)
  }

  const executeImport = async ({ forceDryRun } = {}) => {
    setImportError('')
    setImportResult(null)
    
    if (!importAccount) {
      setImportError('Selecione a conta que receberá as transações importadas.')
      return
    }
    
    if (!importFile) {
      setImportError('Selecione o arquivo .xlsx gerado pelo modelo.')
      return
    }
    
    setImportLoading(true)
    try {
      const effectiveDryRun = typeof forceDryRun === 'boolean' ? forceDryRun : importDryRun
      const formData = new FormData()
      formData.append('account_id', importAccount)
      formData.append('dry_run', effectiveDryRun ? 'true' : 'false')
      formData.append('file', importFile)
      
      const response = await api.post('/transactions/import', formData)
      setImportResult(response.data)
      setLastImportDryRun(effectiveDryRun)
      
      if (!effectiveDryRun) {
        queryClient.invalidateQueries(['transactions'])
        queryClient.invalidateQueries(['dashboard'])
        queryClient.invalidateQueries(['accounts'])
        setImportFile(null)
      }
    } catch (error) {
      setImportError(buildImportErrorMessage(error))
    } finally {
      setImportLoading(false)
    }
  }

  const handleImportSubmit = () => executeImport()
  const handleConfirmImport = () => executeImport({ forceDryRun: false })

  const formatPreviewCurrency = (value, currencyCode = 'BRL') => {
    try {
      return Number(value || 0).toLocaleString('pt-BR', {
        style: 'currency',
        currency: currencyCode || 'BRL'
      })
    } catch {
      const fallback = formatCurrency(value || 0)
      return currencyCode && currencyCode !== 'BRL' ? `${fallback} (${currencyCode})` : fallback
    }
  }

  const handleProfileSave = () => {
    // Implementar salvamento do perfil
    console.log('Salvando perfil:', profile)
  }

  const handlePasswordChange = () => {
    // Implementar mudança de senha
    console.log('Alterando senha')
  }

  const handleNotificationsSave = () => {
    // Implementar salvamento das notificações
    console.log('Salvando notificações:', notifications)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Configurações</h1>
        <p className="text-muted-foreground">
          Gerencie suas preferências e configurações da conta
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="profile">Perfil</TabsTrigger>
          <TabsTrigger value="notifications">Notificações</TabsTrigger>
          <TabsTrigger value="security">Segurança</TabsTrigger>
          <TabsTrigger value="preferences">Preferências</TabsTrigger>
        </TabsList>

        {/* Aba Perfil */}
        <TabsContent value="profile" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Informações Pessoais
              </CardTitle>
              <CardDescription>
                Atualize suas informações básicas de perfil
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome completo</Label>
                  <Input
                    id="nome"
                    value={profile.nome}
                    onChange={(e) => setProfile({...profile, nome: e.target.value})}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({...profile, email: e.target.value})}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="telefone">Telefone</Label>
                  <Input
                    id="telefone"
                    value={profile.telefone}
                    onChange={(e) => setProfile({...profile, telefone: e.target.value})}
                    placeholder="(11) 99999-9999"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="timezone">Fuso horário</Label>
                  <Select value={profile.timezone} onValueChange={(value) => setProfile({...profile, timezone: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="America/Sao_Paulo">São Paulo (GMT-3)</SelectItem>
                      <SelectItem value="America/Manaus">Manaus (GMT-4)</SelectItem>
                      <SelectItem value="America/Rio_Branco">Rio Branco (GMT-5)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="moeda">Moeda padrão</Label>
                  <Select value={profile.moeda} onValueChange={(value) => setProfile({...profile, moeda: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="BRL">Real Brasileiro (R$)</SelectItem>
                      <SelectItem value="USD">Dólar Americano ($)</SelectItem>
                      <SelectItem value="EUR">Euro (€)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="formato_data">Formato de data</Label>
                  <Select value={profile.formato_data} onValueChange={(value) => setProfile({...profile, formato_data: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                      <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                      <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex justify-end">
                <Button onClick={handleProfileSave}>
                  <Save className="h-4 w-4 mr-2" />
                  Salvar alterações
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Notificações */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Preferências de Notificação
              </CardTitle>
              <CardDescription>
                Configure como e quando você quer receber notificações
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium mb-4">Notificações por Email</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Novas transações</Label>
                      <p className="text-sm text-muted-foreground">
                        Receba um email quando uma nova transação for adicionada
                      </p>
                    </div>
                    <Switch
                      checked={notifications.email_transacoes}
                      onCheckedChange={(checked) => setNotifications({...notifications, email_transacoes: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Alertas de orçamento</Label>
                      <p className="text-sm text-muted-foreground">
                        Notificações quando você exceder 80% do orçamento
                      </p>
                    </div>
                    <Switch
                      checked={notifications.email_orcamentos}
                      onCheckedChange={(checked) => setNotifications({...notifications, email_orcamentos: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Vencimentos próximos</Label>
                      <p className="text-sm text-muted-foreground">
                        Lembrete de contas que vencem em 3 dias
                      </p>
                    </div>
                    <Switch
                      checked={notifications.email_vencimentos}
                      onCheckedChange={(checked) => setNotifications({...notifications, email_vencimentos: checked})}
                    />
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h4 className="font-medium mb-4">Notificações Push</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Transações</Label>
                      <p className="text-sm text-muted-foreground">
                        Notificações instantâneas no navegador
                      </p>
                    </div>
                    <Switch
                      checked={notifications.push_transacoes}
                      onCheckedChange={(checked) => setNotifications({...notifications, push_transacoes: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Orçamentos</Label>
                      <p className="text-sm text-muted-foreground">
                        Alertas de orçamento em tempo real
                      </p>
                    </div>
                    <Switch
                      checked={notifications.push_orcamentos}
                      onCheckedChange={(checked) => setNotifications({...notifications, push_orcamentos: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Vencimentos</Label>
                      <p className="text-sm text-muted-foreground">
                        Lembretes de contas a pagar
                      </p>
                    </div>
                    <Switch
                      checked={notifications.push_vencimentos}
                      onCheckedChange={(checked) => setNotifications({...notifications, push_vencimentos: checked})}
                    />
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end">
                <Button onClick={handleNotificationsSave}>
                  <Save className="h-4 w-4 mr-2" />
                  Salvar preferências
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Segurança */}
        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Segurança da Conta
              </CardTitle>
              <CardDescription>
                Gerencie a segurança e privacidade da sua conta
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium mb-4">Alterar Senha</h4>
                <div className="space-y-4 max-w-md">
                  <div className="space-y-2">
                    <Label htmlFor="senha_atual">Senha atual</Label>
                    <div className="relative">
                      <Input
                        id="senha_atual"
                        type={showPassword ? 'text' : 'password'}
                        value={security.senha_atual}
                        onChange={(e) => setSecurity({...security, senha_atual: e.target.value})}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="senha_nova">Nova senha</Label>
                    <Input
                      id="senha_nova"
                      type="password"
                      value={security.senha_nova}
                      onChange={(e) => setSecurity({...security, senha_nova: e.target.value})}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="confirmar_senha">Confirmar nova senha</Label>
                    <Input
                      id="confirmar_senha"
                      type="password"
                      value={security.confirmar_senha}
                      onChange={(e) => setSecurity({...security, confirmar_senha: e.target.value})}
                    />
                  </div>
                  
                  <Button onClick={handlePasswordChange}>
                    Alterar senha
                  </Button>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h4 className="font-medium mb-4">Configurações de Segurança</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Autenticação de dois fatores</Label>
                      <p className="text-sm text-muted-foreground">
                        Adicione uma camada extra de segurança à sua conta
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">Em breve</Badge>
                      <Switch
                        checked={security.two_factor}
                        onCheckedChange={(checked) => setSecurity({...security, two_factor: checked})}
                        disabled
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Notificações de login</Label>
                      <p className="text-sm text-muted-foreground">
                        Receba alertas quando alguém acessar sua conta
                      </p>
                    </div>
                    <Switch
                      checked={security.login_notifications}
                      onCheckedChange={(checked) => setSecurity({...security, login_notifications: checked})}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Preferências */}
        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Aparência e Dados
              </CardTitle>
              <CardDescription>
                Personalize a interface e gerencie seus dados
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium mb-4">Tema da Interface</h4>
                <div className="flex gap-4">
                  <Button
                    variant={theme === 'light' ? 'default' : 'outline'}
                    onClick={() => setTheme('light')}
                  >
                    Claro
                  </Button>
                  <Button
                    variant={theme === 'dark' ? 'default' : 'outline'}
                    onClick={() => setTheme('dark')}
                  >
                    Escuro
                  </Button>
                  <Button
                    variant={theme === 'system' ? 'default' : 'outline'}
                    onClick={() => setTheme('system')}
                  >
                    Sistema
                  </Button>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h4 className="font-medium mb-4">Gerenciamento de Dados</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Exportar dados</Label>
                      <p className="text-sm text-muted-foreground">
                        Baixe uma cópia de todos os seus dados
                      </p>
                    </div>
                    <Button variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      Exportar
                    </Button>
                  </div>

                  <div className="space-y-4 rounded-lg border border-dashed p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div>
                        <Label>Importar dados</Label>
                        <p className="text-sm text-muted-foreground">
                          Importe transações de outros sistemas
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Modelo inclui os campos obrigatórios: tipo, data_lancamento, descricao e valor.
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Use valores em portugues: tipo = receita ou despesa - status = pendente, compensada ou conciliada - payment_method = dinheiro, pix, cartao_debito, cartao_credito, boleto, transferencia, cheque ou outros.
                        </p>
                      </div>
                      <Button variant="ghost" asChild>
                        <a
                          href="/templates/import-transacoes-template.xlsx"
                          download
                          className="inline-flex items-center"
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Baixar modelo
                        </a>
                      </Button>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-2">
                        <Label>Conta de destino</Label>
                        <Select
                          value={importAccount}
                          onValueChange={setImportAccount}
                          disabled={accountsQuery.isLoading || !hasAccounts || importLoading}
                        >
                          <SelectTrigger>
                            <SelectValue
                              placeholder={
                                accountsQuery.isLoading
                                  ? 'Carregando contas...'
                                  : hasAccounts
                                    ? 'Selecione a conta'
                                    : 'Nenhuma conta disponível'
                              }
                            />
                          </SelectTrigger>
                          <SelectContent>
                            {accounts.map((account) => (
                              <SelectItem key={account.id} value={account.id}>
                                {account.nome} ({account.tipo})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {accountsQuery.isError && (
                          <p className="text-xs text-red-600">
                            Não foi possível carregar as contas.
                          </p>
                        )}
                        {!accountsQuery.isLoading && !hasAccounts && (
                          <p className="text-xs text-muted-foreground">
                            Cadastre uma conta antes de importar transações.
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label>Arquivo do modelo (.xlsx)</Label>
                        <Input
                          type="file"
                          accept=".xlsx"
                          onChange={handleImportFileChange}
                          disabled={!hasAccounts || importLoading}
                        />
                        {importFile && (
                          <p className="text-xs text-muted-foreground truncate">
                            Arquivo selecionado: {importFile.name}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div className="flex items-start gap-3">
                        <Switch
                          id="import-dry-run"
                          checked={importDryRun}
                          onCheckedChange={(checked) => setImportDryRun(checked)}
                          disabled={importLoading}
                        />
                        <div>
                          <Label htmlFor="import-dry-run" className="text-sm">Modo teste</Label>
                          <p className="text-xs text-muted-foreground">
                            Valide o arquivo sem criar transações. Desative para importar de fato.
                          </p>
                        </div>
                      </div>
                      <Button
                        onClick={handleImportSubmit}
                        disabled={!hasAccounts || !importAccount || !importFile || importLoading}
                      >
                        {importLoading ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Processando...
                          </>
                        ) : (
                          <>
                            <Upload className="h-4 w-4 mr-2" />
                            {importDryRun ? 'Validar arquivo' : 'Importar agora'}
                          </>
                        )}
                      </Button>
                    </div>

                    {importError && (
                      <Alert variant="destructive">
                        <AlertTitle>Erro ao importar</AlertTitle>
                        <AlertDescription>{importError}</AlertDescription>
                      </Alert>
                    )}

                    {importResult && (
                      <div className="space-y-4">
                        <Alert>
                          <AlertTitle>
                            {lastImportDryRun ? 'Pré-visualização gerada' : 'Importação concluída'}
                          </AlertTitle>
                          <AlertDescription>
                            <div className="grid gap-2 md:grid-cols-2">
                              <p>
                                <span className="font-medium">Total de linhas:</span>{' '}
                                {importResult.total_linhas}
                              </p>
                              <p>
                                <span className="font-medium">Processadas:</span>{' '}
                                {importResult.linhas_processadas}
                              </p>
                              <p>
                                <span className="font-medium">Com erro:</span>{' '}
                                {importResult.linhas_com_erro}
                              </p>
                              <p>
                                <span className="font-medium">Transações criadas:</span>{' '}
                                {importResult.transacoes_criadas}
                              </p>
                            </div>
                            {!lastImportDryRun && (
                              <p className="mt-2 text-xs text-muted-foreground">
                                As transações válidas foram adicionadas à conta selecionada.
                              </p>
                            )}
                          </AlertDescription>
                        </Alert>

                        {importResult.preview?.length > 0 && (
                          <div className="space-y-2">
                            <p className="text-sm font-medium">
                              Prévia das primeiras {importResult.preview.length} linhas
                            </p>
                            <div className="overflow-x-auto rounded-md border">
                              <table className="w-full text-sm">
                                <thead className="bg-muted/40">
                                  <tr>
                                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-muted-foreground">Linha</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-muted-foreground">Data</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-muted-foreground">Descrição</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-muted-foreground">Tipo</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-muted-foreground">Valor</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-muted-foreground">Categoria</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-muted-foreground">Status</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {importResult.preview.map((item) => (
                                    <tr key={item.linha} className="border-t">
                                      <td className="px-3 py-2 text-xs text-muted-foreground">{item.linha}</td>
                                      <td className="px-3 py-2">{item.data_lancamento}</td>
                                      <td className="px-3 py-2">{item.descricao}</td>
                                      <td className="px-3 py-2 capitalize">{item.tipo}</td>
                                      <td className="px-3 py-2">
                                        {formatPreviewCurrency(item.valor, item.moeda)}
                                      </td>
                                      <td className="px-3 py-2">{item.categoria || '—'}</td>
                                      <td className="px-3 py-2 capitalize">{item.status}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {importResult.erros?.length > 0 && (
                          <Alert variant="destructive">
                            <AlertTitle>Linhas com erro ({importResult.erros.length})</AlertTitle>
                            <AlertDescription>
                              <ul className="list-disc space-y-1 pl-5">
                                {importResult.erros.slice(0, 5).map((msg, idx) => (
                                  <li key={`${msg}-${idx}`}>{msg}</li>
                                ))}
                              </ul>
                              {importResult.erros.length > 5 && (
                                <p className="mt-2 text-xs text-muted-foreground">
                                  Mostrando 5 de {importResult.erros.length} erros.
                                </p>
                              )}
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h4 className="font-medium mb-4 text-red-600">Zona de Perigo</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg">
                    <div>
                      <Label className="text-red-600">Excluir conta</Label>
                      <p className="text-sm text-muted-foreground">
                        Exclua permanentemente sua conta e todos os dados
                      </p>
                    </div>
                    <Button variant="destructive">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Excluir conta
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
