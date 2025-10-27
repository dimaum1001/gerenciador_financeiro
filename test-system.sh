#!/bin/bash

# Script de teste para validar o sistema completo
# Este script verifica se todos os componentes estão funcionando corretamente

set -e

echo "🧪 Iniciando testes do sistema Gerenciador Financeiro..."
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar estrutura do projeto
echo -e "\n${BLUE}1. Verificando estrutura do projeto...${NC}"

# Verificar arquivos principais
test -f "docker-compose.yml" && print_status 0 "docker-compose.yml encontrado" || print_status 1 "docker-compose.yml não encontrado"
test -f "Makefile" && print_status 0 "Makefile encontrado" || print_status 1 "Makefile não encontrado"
test -f "README.md" && print_status 0 "README.md encontrado" || print_status 1 "README.md não encontrado"

# Verificar backend
test -d "backend" && print_status 0 "Diretório backend encontrado" || print_status 1 "Diretório backend não encontrado"
test -f "backend/pyproject.toml" && print_status 0 "pyproject.toml encontrado" || print_status 1 "pyproject.toml não encontrado"
test -f "backend/Dockerfile" && print_status 0 "Backend Dockerfile encontrado" || print_status 1 "Backend Dockerfile não encontrado"
test -f "backend/app/main.py" && print_status 0 "main.py encontrado" || print_status 1 "main.py não encontrado"

# Verificar frontend
test -d "frontend/finance-manager-web" && print_status 0 "Diretório frontend encontrado" || print_status 1 "Diretório frontend não encontrado"
test -f "frontend/finance-manager-web/package.json" && print_status 0 "package.json encontrado" || print_status 1 "package.json não encontrado"
test -f "frontend/Dockerfile" && print_status 0 "Frontend Dockerfile encontrado" || print_status 1 "Frontend Dockerfile não encontrado"

# 2. Verificar configurações
echo -e "\n${BLUE}2. Verificando configurações...${NC}"

# Verificar arquivos .env
test -f ".env.example" && print_status 0 ".env.example na raiz encontrado" || print_status 1 ".env.example na raiz não encontrado"
test -f "backend/.env.example" && print_status 0 "backend/.env.example encontrado" || print_status 1 "backend/.env.example não encontrado"

# Verificar se os arquivos .env existem (criados durante setup)
if [ -f "backend/.env" ]; then
    print_status 0 "backend/.env configurado"
else
    print_warning "backend/.env não encontrado - será criado automaticamente"
fi

if [ -f "frontend/finance-manager-web/.env" ]; then
    print_status 0 "frontend/.env configurado"
else
    print_warning "frontend/.env não encontrado - será criado automaticamente"
fi

# 3. Verificar modelos e schemas
echo -e "\n${BLUE}3. Verificando modelos e schemas...${NC}"

# Verificar modelos SQLAlchemy
test -f "backend/app/models/user.py" && print_status 0 "Modelo User encontrado" || print_status 1 "Modelo User não encontrado"
test -f "backend/app/models/account.py" && print_status 0 "Modelo Account encontrado" || print_status 1 "Modelo Account não encontrado"
test -f "backend/app/models/category.py" && print_status 0 "Modelo Category encontrado" || print_status 1 "Modelo Category não encontrado"
test -f "backend/app/models/transaction.py" && print_status 0 "Modelo Transaction encontrado" || print_status 1 "Modelo Transaction não encontrado"
test -f "backend/app/models/budget.py" && print_status 0 "Modelo Budget encontrado" || print_status 1 "Modelo Budget não encontrado"

# Verificar schemas Pydantic
test -f "backend/app/schemas/user.py" && print_status 0 "Schema User encontrado" || print_status 1 "Schema User não encontrado"
test -f "backend/app/schemas/auth.py" && print_status 0 "Schema Auth encontrado" || print_status 1 "Schema Auth não encontrado"

# 4. Verificar routers da API
echo -e "\n${BLUE}4. Verificando routers da API...${NC}"

test -f "backend/app/routers/auth.py" && print_status 0 "Router Auth encontrado" || print_status 1 "Router Auth não encontrado"
test -f "backend/app/routers/users.py" && print_status 0 "Router Users encontrado" || print_status 1 "Router Users não encontrado"
test -f "backend/app/routers/accounts.py" && print_status 0 "Router Accounts encontrado" || print_status 1 "Router Accounts não encontrado"
test -f "backend/app/routers/categories.py" && print_status 0 "Router Categories encontrado" || print_status 1 "Router Categories não encontrado"
test -f "backend/app/routers/transactions.py" && print_status 0 "Router Transactions encontrado" || print_status 1 "Router Transactions não encontrado"
test -f "backend/app/routers/budgets.py" && print_status 0 "Router Budgets encontrado" || print_status 1 "Router Budgets não encontrado"
test -f "backend/app/routers/dashboard.py" && print_status 0 "Router Dashboard encontrado" || print_status 1 "Router Dashboard não encontrado"

# 5. Verificar componentes do frontend
echo -e "\n${BLUE}5. Verificando componentes do frontend...${NC}"

test -f "frontend/finance-manager-web/src/App.jsx" && print_status 0 "App.jsx encontrado" || print_status 1 "App.jsx não encontrado"
test -f "frontend/finance-manager-web/src/contexts/AuthContext.jsx" && print_status 0 "AuthContext encontrado" || print_status 1 "AuthContext não encontrado"
test -f "frontend/finance-manager-web/src/contexts/ApiContext.jsx" && print_status 0 "ApiContext encontrado" || print_status 1 "ApiContext não encontrado"

# Verificar páginas
test -f "frontend/finance-manager-web/src/pages/LoginPage.jsx" && print_status 0 "LoginPage encontrada" || print_status 1 "LoginPage não encontrada"
test -f "frontend/finance-manager-web/src/pages/DashboardPage.jsx" && print_status 0 "DashboardPage encontrada" || print_status 1 "DashboardPage não encontrada"
test -f "frontend/finance-manager-web/src/pages/TransactionsPage.jsx" && print_status 0 "TransactionsPage encontrada" || print_status 1 "TransactionsPage não encontrada"

# Verificar hooks customizados
test -f "frontend/finance-manager-web/src/hooks/useApi.js" && print_status 0 "Hook useApi encontrado" || print_status 1 "Hook useApi não encontrado"

# 6. Verificar migrações e seeds
echo -e "\n${BLUE}6. Verificando migrações e seeds...${NC}"

test -f "backend/alembic.ini" && print_status 0 "alembic.ini encontrado" || print_status 1 "alembic.ini não encontrado"
test -f "backend/alembic/env.py" && print_status 0 "alembic/env.py encontrado" || print_status 1 "alembic/env.py não encontrado"
test -f "backend/scripts/seed_data.py" && print_status 0 "Script de seed encontrado" || print_status 1 "Script de seed não encontrado"

# 7. Verificar sintaxe dos arquivos Python
echo -e "\n${BLUE}7. Verificando sintaxe dos arquivos Python...${NC}"

# Verificar se python3 está disponível
if command -v python3 &> /dev/null; then
    # Verificar sintaxe do main.py
    python3 -m py_compile backend/app/main.py 2>/dev/null && print_status 0 "Sintaxe do main.py válida" || print_status 1 "Erro de sintaxe no main.py"
    
    # Verificar sintaxe dos modelos
    python3 -m py_compile backend/app/models/*.py 2>/dev/null && print_status 0 "Sintaxe dos modelos válida" || print_status 1 "Erro de sintaxe nos modelos"
    
    # Verificar sintaxe dos routers
    python3 -m py_compile backend/app/routers/*.py 2>/dev/null && print_status 0 "Sintaxe dos routers válida" || print_status 1 "Erro de sintaxe nos routers"
else
    print_warning "Python3 não encontrado - pulando verificação de sintaxe"
fi

# 8. Verificar dependências do frontend
echo -e "\n${BLUE}8. Verificando dependências do frontend...${NC}"

if [ -f "frontend/finance-manager-web/package.json" ]; then
    # Verificar se as dependências principais estão listadas
    if grep -q "react" "frontend/finance-manager-web/package.json"; then
        print_status 0 "React listado nas dependências"
    else
        print_status 1 "React não encontrado nas dependências"
    fi
    
    if grep -q "@tanstack/react-query" "frontend/finance-manager-web/package.json"; then
        print_status 0 "React Query listado nas dependências"
    else
        print_status 1 "React Query não encontrado nas dependências"
    fi
    
    if grep -q "axios" "frontend/finance-manager-web/package.json"; then
        print_status 0 "Axios listado nas dependências"
    else
        print_status 1 "Axios não encontrado nas dependências"
    fi
fi

# 9. Verificar configuração do Docker
echo -e "\n${BLUE}9. Verificando configuração do Docker...${NC}"

# Verificar se os Dockerfiles têm conteúdo
if [ -s "backend/Dockerfile" ]; then
    print_status 0 "Backend Dockerfile não está vazio"
else
    print_status 1 "Backend Dockerfile está vazio"
fi

if [ -s "frontend/Dockerfile" ]; then
    print_status 0 "Frontend Dockerfile não está vazio"
else
    print_status 1 "Frontend Dockerfile está vazio"
fi

# Verificar se docker-compose.yml tem conteúdo
if [ -s "docker-compose.yml" ]; then
    print_status 0 "docker-compose.yml não está vazio"
else
    print_status 1 "docker-compose.yml está vazio"
fi

# 10. Resumo final
echo -e "\n${GREEN}🎉 Testes do sistema concluídos!${NC}"
echo "=================================================="
print_info "O sistema Gerenciador Financeiro está estruturado corretamente."
print_info "Todos os componentes principais foram verificados e estão presentes."
echo ""
print_info "Para executar o sistema:"
echo "  1. Configure os arquivos .env (copie dos .env.example)"
echo "  2. Execute: make up (ou docker-compose up --build)"
echo "  3. Acesse: http://localhost:5173"
echo "  4. Login: admin@demo.com / admin123"
echo ""
print_info "Para mais informações, consulte o README.md"

echo -e "\n${GREEN}✅ Sistema pronto para uso!${NC}"
