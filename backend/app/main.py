"""
Aplicação principal FastAPI
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.database import engine
from app.db.session import DatabaseManager, get_db_context
from app.services.demo_data import ensure_demo_user


# Configurar logging estruturado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação
    """
    # Startup
    logger.info("Starting Finance Manager API", version=settings.app_version)
    
    # Verificar conexão com banco
    if not DatabaseManager.check_connection():
        logger.error("Database connection failed")
        raise RuntimeError("Cannot connect to database")
    
    logger.info("Database connection established")

    # Garantir que a estrutura mínima exista (útil após recriar o arquivo SQLite)
    try:
        DatabaseManager.create_tables()
        logger.info("Database schema ready")
        # Garantir que o usuário demo exista com os dados de demonstração necessários
        with get_db_context() as db:
            ensure_demo_user(db)
        logger.info("Demo user ready")
    except Exception:
        logger.exception("Failed to ensure database schema")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Finance Manager API")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    openapi_url="/api/v1/openapi.json" if settings.is_development else None,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan
)


# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# Middleware de hosts confiáveis (produção)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure domínios específicos em produção
    )


# Middleware de logging e request ID
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware para logging de requisições e request ID
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Adicionar request ID ao contexto
    request.state.request_id = request_id
    
    # Log da requisição
    logger.info(
        "Request started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        user_agent=request.headers.get("user-agent"),
        client_ip=request.client.host if request.client else None
    )
    
    try:
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Adicionar headers de resposta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log da resposta
        logger.info(
            "Request completed",
            request_id=request_id,
            status_code=response.status_code,
            process_time=process_time
        )
        
        return response
        
    except Exception as exc:
        process_time = time.time() - start_time
        
        logger.error(
            "Request failed",
            request_id=request_id,
            error=str(exc),
            process_time=process_time,
            exc_info=True
        )
        
        raise


# Handler de exceções globais
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handler para exceções do SQLAlchemy
    """
    logger.error(
        "Database error",
        request_id=getattr(request.state, "request_id", None),
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handler para ValueError
    """
    logger.warning(
        "Value error",
        request_id=getattr(request.state, "request_id", None),
        error=str(exc)
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


# Rotas de saúde
@app.get("/healthz")
def health_check():
    """
    Endpoint de verificação de saúde
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": time.time()
    }


@app.get("/readiness")
def readiness_check():
    """
    Endpoint de verificação de prontidão
    """
    # Verificar conexão com banco
    if not DatabaseManager.check_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not ready"
        )
    
    return {
        "status": "ready",
        "version": settings.app_version,
        "database": "connected"
    }


# Rota raiz
@app.get("/")
def root():
    """
    Endpoint raiz da API
    """
    return {
        "message": "Finance Manager API",
        "version": settings.app_version,
        "docs": "/docs" if settings.is_development else None,
        "health": "/healthz"
    }


# Incluir routers
from app.routers import auth, users, accounts, categories, transactions, budgets, dashboard

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    accounts.router,
    prefix="/api/v1/accounts",
    tags=["Accounts"]
)

app.include_router(
    categories.router,
    prefix="/api/v1/categories",
    tags=["Categories"]
)

app.include_router(
    transactions.router,
    prefix="/api/v1/transactions",
    tags=["Transactions"]
)

app.include_router(
    budgets.router,
    prefix="/api/v1/budgets",
    tags=["Budgets"]
)

app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


# Rota para informações da API
@app.get("/api/v1/info")
def api_info():
    """
    Informações da API
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "environment": settings.environment,
        "timezone": settings.timezone,
        "features": {
            "import": settings.enable_import,
            "export": settings.enable_export,
            "attachments": settings.enable_attachments,
            "recurring": settings.enable_recurring,
            "budgets": settings.enable_budgets
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
