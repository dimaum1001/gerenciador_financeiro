import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useApi } from '@/contexts/ApiContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Eye, EyeOff, DollarSign, TrendingUp, PieChart, BarChart3 } from 'lucide-react'
import LoadingSpinner from '@/components/ui/loading-spinner'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [isRegistering, setIsRegistering] = useState(false)
  const [nome, setNome] = useState('')
  const [confirmSenha, setConfirmSenha] = useState('')
  const [registerError, setRegisterError] = useState('')
  const [registerSuccess, setRegisterSuccess] = useState('')
  const [registerLoading, setRegisterLoading] = useState(false)

  const { login } = useAuth()
  const { api } = useApi()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const result = await login(email, senha)
    if (!result.success) {
      setError(result.error)
    }

    setLoading(false)
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setRegisterError('')
    setRegisterSuccess('')

    if (!nome.trim()) {
      setRegisterError('Informe seu nome')
      return
    }

    if (senha.length < 8) {
      setRegisterError('A senha deve ter pelo menos 8 caracteres')
      return
    }

    if (senha !== confirmSenha) {
      setRegisterError('As senhas não coincidem')
      return
    }

    setRegisterLoading(true)
    try {
      await api.post('/users', {
        nome,
        email,
        senha,
      })
      setRegisterSuccess('Conta criada com sucesso! Entrando...')
      const result = await login(email, senha)
      if (!result.success) {
        setRegisterError(result.error)
      }
    } catch (err) {
      const message = err.response?.data?.detail || 'Não foi possível criar a conta'
      setRegisterError(message)
    } finally {
      setRegisterLoading(false)
    }
  }

  const toggleMode = () => {
    setIsRegistering((prev) => !prev)
    setError('')
    setRegisterError('')
    setRegisterSuccess('')
    setRegisterLoading(false)
    if (!isRegistering) {
      // ao entrar no modo cadastro, limpamos dados sensíveis
      setNome('')
      setSenha('')
      setConfirmSenha('')
      setEmail('')
      setShowPassword(false)
    } else {
      setEmail('')
      setSenha('')
      setShowPassword(false)
    }
  }

  const renderLoginForm = () => (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="seu@email.com"
          required
          className="h-11"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="senha">Senha</Label>
        <div className="relative">
          <Input
            id="senha"
            type={showPassword ? 'text' : 'password'}
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            placeholder="Sua senha"
            required
            className="h-11 pr-10"
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? (
              <EyeOff className="h-4 w-4 text-muted-foreground" />
            ) : (
              <Eye className="h-4 w-4 text-muted-foreground" />
            )}
          </Button>
        </div>
      </div>

      <Button
        type="submit"
        className="w-full h-11 text-base font-medium"
        disabled={loading}
      >
        {loading ? (
          <>
            <LoadingSpinner size="sm" className="mr-2" />
            Entrando...
          </>
        ) : (
          'Entrar'
        )}
      </Button>
    </form>
  )

  const renderRegisterForm = () => (
    <form onSubmit={handleRegister} className="space-y-6">
      {registerError && (
        <Alert variant="destructive">
          <AlertDescription>{registerError}</AlertDescription>
        </Alert>
      )}

      {registerSuccess && (
        <Alert>
          <AlertDescription className="text-green-600">{registerSuccess}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="nome">Nome completo</Label>
        <Input
          id="nome"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          placeholder="Seu nome"
          required
          className="h-11"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="cadastro-email">Email</Label>
        <Input
          id="cadastro-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="seu@email.com"
          required
          className="h-11"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="cadastro-senha">Senha</Label>
        <Input
          id="cadastro-senha"
          type="password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          placeholder="Mínimo de 8 caracteres"
          required
          className="h-11"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="cadastro-confirmar-senha">Confirmar senha</Label>
        <Input
          id="cadastro-confirmar-senha"
          type="password"
          value={confirmSenha}
          onChange={(e) => setConfirmSenha(e.target.value)}
          placeholder="Repita a senha"
          required
          className="h-11"
        />
      </div>

      <Button
        type="submit"
        className="w-full h-11 text-base font-medium"
        disabled={registerLoading}
      >
        {registerLoading ? (
          <>
            <LoadingSpinner size="sm" className="mr-2" />
            Criando conta...
          </>
        ) : (
          'Criar conta'
        )}
      </Button>
    </form>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex">
      {/* Lado esquerdo */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-green-600 p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full"></div>
        <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-white/5 rounded-full"></div>

        <div className="relative z-10 flex flex-col justify-center">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-white/20 rounded-xl">
                <DollarSign className="h-8 w-8" />
              </div>
              <h1 className="text-3xl font-bold">Gerenciador Financeiro</h1>
            </div>
            <p className="text-xl text-blue-100 mb-8">
              Controle completo das suas finanças pessoais e empresariais
            </p>
          </div>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="p-2 bg-white/20 rounded-lg">
                <TrendingUp className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">Dashboard Inteligente</h3>
                <p className="text-blue-100">
                  Visualize seus gastos, receitas e tendências em tempo real
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-2 bg-white/20 rounded-lg">
                <PieChart className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">Categoriação Automática</h3>
                <p className="text-blue-100">
                  Organize suas transações por categorias hierárquicas
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-2 bg-white/20 rounded-lg">
                <BarChart3 className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">Orçamentos e Metas</h3>
                <p className="text-blue-100">
                  Defina orçamentos mensais e acompanhe seu progresso
                </p>
              </div>
            </div>
          </div>

          <div className="mt-12 p-6 bg-white/10 rounded-xl border border-white/20">
            <h4 className="font-semibold mb-2">Dados de Demonstração</h4>
            <p className="text-sm text-blue-100 mb-3">
              Prefere testar com dados fictícios? Use uma conta demonstrativa ou crie a sua.
            </p>
            <div className="space-y-1 text-sm font-mono">
              <div>Email demo: <span className="text-yellow-200">admin@demo.com</span></div>
              <div>Senha demo: <span className="text-yellow-200">admin123</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* Lado direito */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Card className="shadow-xl border-0">
            <CardHeader className="text-center pb-8">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-blue-100 rounded-xl">
                  <DollarSign className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <CardTitle className="text-2xl font-bold">
                {isRegistering ? 'Crie sua conta' : 'Bem-vindo de volta'}
              </CardTitle>
              <CardDescription>
                {isRegistering
                  ? 'Leva menos de um minuto para começar a organizar suas finanças'
                  : 'Entre com suas credenciais para acessar sua conta'}
              </CardDescription>
            </CardHeader>

            <CardContent>
              {isRegistering ? renderRegisterForm() : renderLoginForm()}

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  {isRegistering ? 'Já tem uma conta?' : 'Ainda não possui conta?'}{' '}
                  <Button
                    type="button"
                    variant="link"
                    className="px-1"
                    onClick={toggleMode}
                  >
                    {isRegistering ? 'Faça login' : 'Criar uma conta'}
                  </Button>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
