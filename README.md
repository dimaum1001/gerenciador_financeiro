'''
# Gerenciador Financeiro - MVP Completo

![Dashboard](https://raw.githubusercontent.com/your-username/finance-manager-mvp/main/docs/dashboard.png)

Este é um projeto MVP (Minimum Viable Product) de um **Gerenciador Financeiro** completo, construído com uma stack moderna e robusta. O sistema permite o controle de finanças pessoais e empresariais, com funcionalidades avançadas de categorização, orçamentos, relatórios e um dashboard interativo.

Este projeto foi desenvolvido como uma demonstração de capacidade técnica, seguindo as melhores práticas de desenvolvimento de software, incluindo arquitetura limpa, containerização com Docker, testes automatizados e uma interface de usuário profissional.

## ✨ Funcionalidades Principais

- **Dashboard Interativo:** Visão geral completa com fluxo de caixa, distribuição de gastos, saldos de contas e próximos vencimentos.
- **Gestão Multi-Conta:** Suporte para contas correntes, poupança, investimentos, cartões de crédito e dinheiro.
- **Categorização Hierárquica:** Organize receitas e despesas com categorias e subcategorias personalizáveis.
- **Sistema de Orçamentos:** Crie orçamentos mensais por categoria e acompanhe o progresso com indicadores visuais.
- **Transações Detalhadas:** Registre receitas, despesas e transferências com suporte a parcelas e anexos.
- **Filtros Avançados:** Busque e filtre transações por múltiplos critérios com paginação server-side.
- **Relatórios Gráficos:** Análises de fluxo de caixa, evolução do patrimônio e comparativos anuais.
- **Autenticação JWT:** Sistema de autenticação seguro com usuário de demonstração.
- **Design Responsivo:** Interface moderna e adaptável para desktop e dispositivos móveis.
- **Tema Claro e Escuro:** Personalize a aparência da aplicação.

## 🚀 Stack Tecnológica

| Camada        | Tecnologia                                                                                                  |
|---------------|-------------------------------------------------------------------------------------------------------------|
| **Backend**   | **FastAPI**, **SQLAlchemy 2.0**, **Pydantic v2**, **Alembic**, **SQLite (dev)** / **PostgreSQL 15 (prod)**     |
| **Frontend**  | **React**, **Vite**, **Tailwind CSS**, **shadcn/ui**, **Recharts**, **React Query**                             |
| **Infra**     | **Docker Compose**, **Nginx**, **Gunicorn**, **Redis**                                                        |
| **Auth**      | **JWT (JSON Web Tokens)** com `python-jose`                                                                 |
| **Testes**    | **Pytest** (backend), **Vitest** (frontend)                                                                 |
| **Linting**   | **Ruff**, **ESLint**, **Prettier**                                                                          |

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas em sua máquina:

- **Python 3.11+** e **pip** (para executar localmente com SQLite via VSCode)
- **Docker:** [https://www.docker.com/get-started](https://www.docker.com/get-started) *(opcional, apenas se quiser usar containers)*
- **Docker Compose:** (opcional, acompanha o Docker Desktop)
- **Make:** (opcional, para usar os comandos do `Makefile`)

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### 1. Clone o Repositório

```bash
git clone https://github.com/your-username/finance-manager-mvp.git
cd finance-manager-mvp
```

### 2. Configure as Variáveis de Ambiente

O projeto utiliza arquivos `.env` para gerenciar as configurações. Existem arquivos de exemplo na raiz e nos diretórios `backend` e `frontend`.

**a. Arquivo Principal (`.env`):**

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Este arquivo define as senhas do banco de dados e outras configurações globais usadas pelo Docker Compose.

**b. Backend (`backend/.env`):**

```bash
cp backend/.env.example backend/.env
```

**c. Frontend (`frontend/finance-manager-web/.env`):**

```bash
cp frontend/finance-manager-web/.env.example frontend/finance-manager-web/.env
```

### 3. Execute o Backend localmente com SQLite (opcional)

Esta � a forma mais r�pida de rodar a API diretamente pelo VSCode, usando o banco `SQLite`.

1. Ative um ambiente virtual na pasta `backend`:

   ```bash
   cd backend
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

2. Instale as dependências do backend:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   # Opcional: ferramentas de teste e lint
   pip install -r requirements-dev.txt
   ```

3. Garanta que o arquivo `backend/.env` exista (passo 2 acima) e aplique as migra��es para criar o banco `SQLite`:

   ```bash
   alembic upgrade head
   ```

   Isso vai gerar o arquivo `storage/finance.db` dentro de `backend/`.

4. Suba a API com o Uvicorn (pode ser via terminal integrado do VSCode ou uma configura��o de debug):

   ```bash
   uvicorn app.main:app --reload
   ```

   A API ficar� dispon�vel em [http://localhost:8000](http://localhost:8000) e a documenta��o interativa em [http://localhost:8000/docs](http://localhost:8000/docs).

### 4. Construa e Inicie os Containers

Com o Docker e Docker Compose instalados, você pode usar o `Makefile` para simplificar o processo. O comando `make up` irá construir as imagens, iniciar os containers, aplicar as migrações do banco e popular com dados de exemplo.

```bash
make up
```

Alternativamente, você pode usar o `docker-compose` diretamente:

```bash
docker-compose up --build -d
```

Após a inicialização, os seguintes serviços estarão disponíveis:

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
- **Documentação da API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 🔑 Acesso de Demonstração

O sistema é populado com dados de exemplo para facilitar a demonstração. Use as seguintes credenciais para acessar:

- **Email:** `admin@demo.com`
- **Senha:** `admin123`

## 🛠️ Comandos Úteis (Makefile)

O `Makefile` na raiz do projeto fornece comandos para gerenciar o ciclo de vida da aplicação:

- `make up`: Constrói e sobe todos os serviços em modo detached.
- `make down`: Para todos os serviços.
- `make build`: Força a reconstrução das imagens e sobe os serviços.
- `make logs`: Exibe os logs de todos os serviços em tempo real.
- `make logs-api`: Exibe os logs apenas do serviço da API.
- `make logs-web`: Exibe os logs apenas do serviço do frontend.
- `make seed`: Executa o script para popular o banco de dados com dados de exemplo.
- `make migrate`: Aplica as migrações do banco de dados.
- `make revision`: Cria uma nova revisão de migração com Alembic.
- `make test-api`: Executa os testes do backend.
- `make clean`: Remove todos os containers, redes e volumes (cuidado, isso apaga os dados do banco).

## 📂 Estrutura do Projeto

```
finance-manager/
├── backend/               # Código fonte do FastAPI
│   ├── alembic/           # Migrações do banco
│   ├── app/               # Lógica da aplicação
│   │   ├── core/          # Configurações, segurança, dependências
│   │   ├── db/            # Conexão e sessão do banco
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── routers/       # Endpoints da API
│   │   ├── schemas/       # Schemas Pydantic
│   │   └── services/      # Lógica de negócio
│   ├── scripts/           # Scripts de seed e inicialização
│   ├── tests/             # Testes Pytest
│   ├── alembic.ini
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/              # Código fonte do React
│   ├── finance-manager-web/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── assets/
│   │   │   ├── components/  # Componentes shadcn/ui e customizados
│   │   │   ├── contexts/    # Contextos React (Auth, API)
│   │   │   ├── hooks/       # Hooks customizados (useApi)
│   │   │   ├── lib/         # Utilitários
│   │   │   └── pages/       # Páginas da aplicação
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── .env.example
├── docker-compose.yml     # Configuração para desenvolvimento
├── docker-compose.prod.yml  # Configuração para produção
├── Makefile
└── README.md
```

## 📚 Documentação da API

A API FastAPI gera documentação interativa automaticamente.

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Todos os endpoints são protegidos e requerem um token JWT, que pode ser obtido através do endpoint de login e inserido na interface do Swagger para autorização.

## 🚀 Deploy em Produção

O arquivo `docker-compose.prod.yml` contém uma configuração otimizada para produção, que inclui:

- **Nginx** como reverse proxy para o frontend e backend.
- **Gunicorn** para servir a aplicação FastAPI com múltiplos workers.
- Remoção de hot-reload e otimizações de build.

Para executar em modo de produção:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 🤝 Contribuições

Este é um projeto de demonstração, mas sinta-se à vontade para clonar, modificar e usar como base para seus próprios projetos. Pull requests com melhorias são bem-vindos!

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
'''


