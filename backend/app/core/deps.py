"""
Dependências da aplicação
"""

import uuid
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User


# Security scheme
security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency para obter usuário atual autenticado
    
    Args:
        db: Sessão do banco de dados
        credentials: Credenciais do token Bearer
        
    Returns:
        User: Usuário autenticado
        
    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verificar token
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception
    
    # Buscar usuário no banco
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise credentials_exception
    
    # Verificar se usuário está ativo
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def get_current_non_demo_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency que bloqueia opera����es de escrita para usuǭrios demo.
    """
    if current_user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário de demonstração possui acesso somente leitura"
        )
    return current_user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para obter usuário ativo
    
    Args:
        current_user: Usuário atual
        
    Returns:
        User: Usuário ativo
        
    Raises:
        HTTPException: Se usuário inativo
    """
    if not current_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para obter usuário com email verificado
    
    Args:
        current_user: Usuário atual
        
    Returns:
        User: Usuário verificado
        
    Raises:
        HTTPException: Se email não verificado
    """
    if not current_user.email_verificado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


class CommonQueryParams:
    """Parâmetros comuns de query para paginação e ordenação"""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        self.page = max(1, page)
        self.per_page = min(100, max(1, per_page))  # Máximo 100 itens por página
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order.lower() in ["asc", "desc"] else "asc"
        
    @property
    def offset(self) -> int:
        """Calcula offset para paginação"""
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        """Retorna limite para paginação"""
        return self.per_page


def get_pagination_params(
    page: int = 1,
    per_page: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> CommonQueryParams:
    """
    Dependency para parâmetros de paginação
    
    Args:
        page: Número da página (padrão: 1)
        per_page: Itens por página (padrão: 20, máximo: 100)
        sort_by: Campo para ordenação
        sort_order: Ordem (asc/desc, padrão: asc)
        
    Returns:
        CommonQueryParams: Parâmetros de paginação
    """
    return CommonQueryParams(page, per_page, sort_by, sort_order)


def get_optional_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Dependency para obter usuário opcional (para endpoints públicos)
    
    Args:
        db: Sessão do banco de dados
        credentials: Credenciais opcionais
        
    Returns:
        Optional[User]: Usuário se autenticado, None caso contrário
    """
    if not credentials:
        return None
    
    try:
        user_id = verify_token(credentials.credentials)
        if user_id is None:
            return None
        
        user_uuid = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
        
        return user if user and user.ativo else None
    except Exception:
        return None
