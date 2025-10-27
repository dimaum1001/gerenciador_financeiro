import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
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
  EyeOff
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/components/theme-provider'

export default function SettingsPage() {
  const { user } = useAuth()
  const { theme, setTheme } = useTheme()
  const [showPassword, setShowPassword] = useState(false)
  
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
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Importar dados</Label>
                      <p className="text-sm text-muted-foreground">
                        Importe transações de outros sistemas
                      </p>
                    </div>
                    <Button variant="outline">
                      <Upload className="h-4 w-4 mr-2" />
                      Importar
                    </Button>
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
