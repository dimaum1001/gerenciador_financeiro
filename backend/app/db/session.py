"""
Gerenciamento de sessões do banco de dados
"""

from typing import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados
    
    Yields:
        Session: Sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager para sessão do banco de dados
    
    Yields:
        Session: Sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseManager:
    """Gerenciador de operações do banco de dados"""
    
    @staticmethod
    def create_tables():
        """Cria todas as tabelas do banco"""
        from app.db.database import engine, Base

        # Para bancos relacionais gerenciados (PostgreSQL, etc.), assumimos que
        # as migrações Alembic cuidam do schema. Evita introspecção pesada no startup.
        if engine.dialect.name != "sqlite":
            return

        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_tables():
        """Remove todas as tabelas do banco"""
        from app.db.database import engine, Base
        Base.metadata.drop_all(bind=engine)
    
    @staticmethod
    def reset_database():
        """Reseta o banco de dados (drop + create)"""
        DatabaseManager.drop_tables()
        DatabaseManager.create_tables()
    
    @staticmethod
    def check_connection() -> bool:
        """
        Verifica se a conexão com o banco está funcionando
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        try:
            with get_db_context() as db:
                db.execute(text("SELECT 1"))
                return True
        except Exception:
            return False
