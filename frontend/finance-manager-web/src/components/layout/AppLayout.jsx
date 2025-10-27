import { useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import {
  LayoutDashboard,
  ArrowUpDown,
  Wallet,
  Tags,
  Target,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  DollarSign,
  Moon,
  Sun,
  User
} from 'lucide-react'
import { useTheme } from '@/components/theme-provider'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Visão geral das finanças'
  },
  {
    name: 'Transações',
    href: '/transactions',
    icon: ArrowUpDown,
    description: 'Receitas e despesas'
  },
  {
    name: 'Contas',
    href: '/accounts',
    icon: Wallet,
    description: 'Contas bancárias e cartões'
  },
  {
    name: 'Categorias',
    href: '/categories',
    icon: Tags,
    description: 'Organização por categorias'
  },
  {
    name: 'Orçamentos',
    href: '/budgets',
    icon: Target,
    description: 'Metas e planejamento'
  },
  {
    name: 'Relatórios',
    href: '/reports',
    icon: BarChart3,
    description: 'Análises e gráficos'
  },
  {
    name: 'Configurações',
    href: '/settings',
    icon: Settings,
    description: 'Preferências do sistema'
  }
]

function Sidebar({ className = '' }) {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-4 border-b">
        <div className="p-2 bg-blue-600 rounded-lg">
          <DollarSign className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-lg">FinanceManager</h1>
          <p className="text-xs text-muted-foreground">MVP v1.0</p>
        </div>
      </div>

      {/* Navegação */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          const Icon = item.icon
          
          return (
            <Button
              key={item.name}
              variant={isActive ? 'default' : 'ghost'}
              className={`w-full justify-start h-auto p-3 ${
                isActive 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'hover:bg-muted'
              }`}
              onClick={() => navigate(item.href)}
            >
              <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
              <div className="text-left">
                <div className="font-medium">{item.name}</div>
                <div className={`text-xs ${
                  isActive ? 'text-blue-100' : 'text-muted-foreground'
                }`}>
                  {item.description}
                </div>
              </div>
            </Button>
          )
        })}
      </nav>

    </div>
  )
}

function Header() {
  const { user, logout } = useAuth()
  const { theme, setTheme } = useTheme()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
  }

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-6">
        {/* Menu mobile */}
        <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="sm" className="lg:hidden mr-2">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 w-80">
            <Sidebar />
          </SheetContent>
        </Sheet>

        {/* Título da página */}
        <div className="flex-1">
          <h2 className="text-lg font-semibold">
            {navigation.find(item => item.href === location.pathname)?.name || 'Dashboard'}
          </h2>
        </div>

        {/* Ações do header */}
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={toggleTheme}>
            {theme === 'light' ? (
              <Moon className="h-4 w-4" />
            ) : (
              <Sun className="h-4 w-4" />
            )}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                <Avatar className="h-9 w-9">
                  <AvatarImage src={user?.avatar_url} alt={user?.nome} />
                  <AvatarFallback>
                    {user?.nome?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user?.nome}</p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user?.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Perfil</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Configurações</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Sair</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar desktop */}
      <aside className="hidden lg:flex lg:w-80 lg:flex-col border-r">
        <Sidebar />
      </aside>

      {/* Conteúdo principal */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
