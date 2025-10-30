"""
Módulo de segurança e autenticação JWT
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings


# Contexto para hash de senhas (usa bcrypt reforçado com SHA-256 para evitar limite de 72 bytes)
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def create_access_token(
    subject: Union[str, uuid.UUID], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria token JWT de acesso
    
    Args:
        subject: ID do usuário ou email
        expires_delta: Tempo de expiração customizado
        
    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verifica e decodifica token JWT
    
    Args:
        token: Token JWT para verificar
        
    Returns:
        Subject (user_id) se válido, None caso contrário
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            return None
            
        return user_id
        
    except (JWTError, ValidationError):
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenado
        
    Returns:
        True se as senhas correspondem, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera hash da senha
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """
    Gera token para reset de senha
    
    Args:
        email: Email do usuário
        
    Returns:
        Token para reset de senha
    """
    delta = timedelta(hours=24)  # Token válido por 24 horas
    now = datetime.utcnow()
    expires = now + delta
    
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verifica token de reset de senha
    
    Args:
        token: Token de reset
        
    Returns:
        Email do usuário se válido, None caso contrário
    """
    try:
        decoded_token = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        email = decoded_token.get("sub")
        token_type = decoded_token.get("type")
        
        if token_type != "password_reset":
            return None
            
        return email
        
    except JWTError:
        return None


def create_api_key() -> str:
    """
    Gera chave de API única
    
    Returns:
        Chave de API
    """
    return f"fmgr_{uuid.uuid4().hex}"


class SecurityUtils:
    """Utilitários de segurança"""
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Valida força da senha
        
        Args:
            password: Senha para validar
            
        Returns:
            True se a senha é forte o suficiente
        """
        if len(password) < 8:
            return False
            
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza nome de arquivo para upload
        
        Args:
            filename: Nome do arquivo original
            
        Returns:
            Nome do arquivo sanitizado
        """
        import re
        
        # Remove caracteres perigosos
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Remove espaços múltiplos
        filename = re.sub(r'\s+', '_', filename)
        
        # Limita tamanho
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = f"{name[:95]}.{ext}" if ext else name[:100]
        
        return filename.lower()
    
    @staticmethod
    def is_safe_redirect_url(url: str) -> bool:
        """
        Verifica se URL de redirecionamento é segura
        
        Args:
            url: URL para verificar
            
        Returns:
            True se a URL é segura
        """
        if not url:
            return False
            
        # Permite apenas URLs relativas ou do mesmo domínio
        if url.startswith('/'):
            return True
            
        # Adicione aqui domínios permitidos se necessário
        allowed_domains = ['localhost', '127.0.0.1']
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        return parsed.netloc in allowed_domains
