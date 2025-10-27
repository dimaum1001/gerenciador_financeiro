# Makefile para Gerenciador Financeiro MVP
.PHONY: help up down build logs clean seed test restart status

# Variáveis
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = finance

help: ## Exibe esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Sobe todos os serviços em background
	@echo "🚀 Subindo todos os serviços..."
	docker compose -f $(COMPOSE_FILE) up -d

build: ## Reconstrói as imagens e sobe os serviços
	@echo "🔨 Reconstruindo imagens e subindo serviços..."
	docker compose -f $(COMPOSE_FILE) up --build -d

down: ## Para todos os serviços
	@echo "🛑 Parando todos os serviços..."
	docker compose -f $(COMPOSE_FILE) down

restart: ## Reinicia todos os serviços
	@echo "🔄 Reiniciando todos os serviços..."
	docker compose -f $(COMPOSE_FILE) restart

logs: ## Exibe logs de todos os serviços
	@echo "📋 Exibindo logs..."
	docker compose -f $(COMPOSE_FILE) logs -f

logs-api: ## Exibe logs apenas do backend
	@echo "📋 Exibindo logs do backend..."
	docker compose -f $(COMPOSE_FILE) logs -f api

logs-web: ## Exibe logs apenas do frontend
	@echo "📋 Exibindo logs do frontend..."
	docker compose -f $(COMPOSE_FILE) logs -f web

logs-db: ## Exibe logs apenas do banco
	@echo "📋 Exibindo logs do banco..."
	docker compose -f $(COMPOSE_FILE) logs -f db

status: ## Mostra status dos serviços
	@echo "📊 Status dos serviços:"
	docker compose -f $(COMPOSE_FILE) ps

seed: ## Executa seeds do banco de dados
	@echo "🌱 Executando seeds do banco..."
	docker compose -f $(COMPOSE_FILE) exec api python scripts/seed_data.py

shell-api: ## Acessa shell do container da API
	@echo "🐚 Acessando shell do backend..."
	docker compose -f $(COMPOSE_FILE) exec api bash

shell-db: ## Acessa shell do PostgreSQL
	@echo "🐚 Acessando shell do banco..."
	docker compose -f $(COMPOSE_FILE) exec db psql -U postgres -d finance

migrate: ## Executa migrações do banco
	@echo "🗃️ Executando migrações..."
	docker compose -f $(COMPOSE_FILE) exec api python -m alembic upgrade head

migrate-create: ## Cria nova migração (usar: make migrate-create MSG="descrição")
	@echo "🗃️ Criando nova migração..."
	docker compose -f $(COMPOSE_FILE) exec api python -m alembic revision --autogenerate -m "$(MSG)"

test: ## Executa testes do backend
	@echo "🧪 Executando testes..."
	docker compose -f $(COMPOSE_FILE) exec api python -m pytest tests/ -v

test-coverage: ## Executa testes com cobertura
	@echo "🧪 Executando testes com cobertura..."
	docker compose -f $(COMPOSE_FILE) exec api python -m pytest tests/ --cov=app --cov-report=html

clean: ## Remove containers, volumes e imagens
	@echo "🧹 Limpando containers, volumes e imagens..."
	docker compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

clean-volumes: ## Remove apenas os volumes
	@echo "🧹 Removendo volumes..."
	docker compose -f $(COMPOSE_FILE) down -v

install: ## Instala dependências (primeira execução)
	@echo "📦 Instalando dependências..."
	@echo "Criando arquivos .env..."
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; fi
	@if [ ! -f frontend/.env ]; then cp frontend/.env.example frontend/.env; fi
	@echo "✅ Projeto configurado! Execute 'make up' para iniciar."

dev: ## Modo desenvolvimento (rebuild + up + logs)
	@echo "🔧 Iniciando modo desenvolvimento..."
	make build
	make logs

prod-build: ## Build para produção
	@echo "🏭 Construindo para produção..."
	docker compose -f $(COMPOSE_FILE) -f docker-compose.prod.yml build

backup-db: ## Faz backup do banco de dados
	@echo "💾 Fazendo backup do banco..."
	docker compose -f $(COMPOSE_FILE) exec db pg_dump -U postgres -d finance > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaura backup do banco (usar: make restore-db FILE=backup.sql)
	@echo "📥 Restaurando backup do banco..."
	docker compose -f $(COMPOSE_FILE) exec -T db psql -U postgres -d finance < $(FILE)

health: ## Verifica saúde dos serviços
	@echo "🏥 Verificando saúde dos serviços..."
	@echo "Database:"
	@curl -s http://localhost:8000/healthz | jq . || echo "❌ API não está respondendo"
	@echo "\nAPI:"
	@docker compose -f $(COMPOSE_FILE) exec db pg_isready -U postgres -d finance || echo "❌ Database não está pronto"
	@echo "\nFrontend:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200" && echo "✅ Frontend OK" || echo "❌ Frontend não está respondendo"

urls: ## Mostra URLs importantes
	@echo "🔗 URLs importantes:"
	@echo "Frontend: http://localhost:5173"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "API Health: http://localhost:8000/healthz"
	@echo "Redoc: http://localhost:8000/redoc"
	@echo ""
	@echo "👤 Login demo:"
	@echo "Email: admin@demo.com"
	@echo "Senha: admin123"
