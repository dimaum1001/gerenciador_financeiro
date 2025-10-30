from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.deps import get_current_user, get_current_non_demo_user, get_db
from app.models.user import User
from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse

router = APIRouter()


def _category_query(db: Session, current_user: User):
    return db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.is_demo_data.is_(current_user.is_demo),
    )

@router.get("/", response_model=CategoryListResponse)
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    parent_id: Optional[str] = None,
    ativo: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar categorias do usuário com filtros opcionais"""
    query = _category_query(db, current_user)
    
    # Aplicar filtros
    if tipo:
        try:
            tipo_enum = CategoryType(tipo)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de categoria inválido",
            )
        query = query.filter(Category.tipo == tipo_enum)
    
    if parent_id:
        query = query.filter(Category.parent_id == parent_id)
    elif parent_id is None:
        # Se não especificado, mostrar apenas categorias raiz
        query = query.filter(Category.parent_id.is_(None))
    
    if ativo is not None:
        query = query.filter(Category.ativo == ativo)
    
    if search:
        query = query.filter(
            or_(
                Category.nome.ilike(f"%{search}%"),
                Category.descricao.ilike(f"%{search}%")
            )
        )
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação e ordenação
    categories = query.order_by(Category.nome).offset(skip).limit(limit).all()
    
    return CategoryListResponse(
        categories=categories,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Criar nova categoria"""
    # Verificar se já existe categoria com mesmo nome no mesmo nível
    existing = (
        _category_query(db, current_user)
        .filter(
            and_(
                Category.nome == category_data.nome,
                Category.parent_id == category_data.parent_id,
            )
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma categoria com este nome no mesmo nível"
        )
    
    # Verificar se categoria pai existe (se especificada)
    if category_data.parent_id:
        parent = (
            _category_query(db, current_user)
            .filter(Category.id == category_data.parent_id)
            .first()
        )
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria pai não encontrada"
            )
        
        # Verificar se tipos são compatíveis
        if parent.tipo != category_data.tipo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo da subcategoria deve ser igual ao da categoria pai"
            )
    
    # Criar categoria
    category = Category(
        **category_data.model_dump(),
        user_id=current_user.id,
        is_demo_data=current_user.is_demo
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter categoria específica"""
    category = _category_query(db, current_user).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Atualizar categoria"""
    category = _category_query(db, current_user).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Verificar nome duplicado (se alterado)
    if category_data.nome and category_data.nome != category.nome:
        existing = (
            _category_query(db, current_user)
            .filter(
                and_(
                    Category.nome == category_data.nome,
                    Category.parent_id == category.parent_id,
                    Category.id != category_id,
                )
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma categoria com este nome no mesmo nível"
            )
    
    # Atualizar campos
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Excluir categoria (soft delete)"""
    category = _category_query(db, current_user).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Verificar se há subcategorias
    subcategories = _category_query(db, current_user).filter(Category.parent_id == category_id).first()
    if subcategories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir categoria que possui subcategorias"
        )
    
    # Verificar se há transações vinculadas
    from app.models.transaction import Transaction
    has_transactions = db.query(Transaction).filter(
        Transaction.category_id == category_id
    ).first()
    
    if has_transactions:
        # Soft delete - apenas desativar
        category.ativo = False
        db.commit()
    else:
        # Hard delete se não há transações
        db.delete(category)
        db.commit()

@router.get("/{category_id}/subcategories", response_model=List[CategoryResponse])
async def get_subcategories(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter subcategorias de uma categoria"""
    # Verificar se categoria pai existe
    parent = _category_query(db, current_user).filter(Category.id == category_id).first()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Buscar subcategorias
    subcategories = (
        _category_query(db, current_user)
        .filter(Category.parent_id == category_id)
        .order_by(Category.nome)
        .all()
    )
    
    return subcategories

@router.get("/tree/{tipo}")
async def get_category_tree(
    tipo: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter árvore hierárquica de categorias"""
    try:
        tipo_enum = CategoryType(tipo)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo deve ser 'income' ou 'expense'",
        )
    
    categories = (
        db.query(Category)
        .filter(
            and_(
                Category.user_id == current_user.id,
                Category.is_demo_data.is_(current_user.is_demo),
                Category.tipo == tipo_enum,
                Category.ativo.is_(True),
            )
        )
        .order_by(Category.nome)
        .all()
    )
    
    # Construir árvore
    def build_tree(parent_id=None):
        tree = []
        for cat in categories:
            if cat.parent_id == parent_id:
                node = {
                    "id": str(cat.id),
                    "nome": cat.nome,
                    "cor": cat.cor,
                    "icone": cat.icone,
                    "descricao": cat.descricao,
                    "children": build_tree(cat.id)
                }
                tree.append(node)
        return tree
    
    return build_tree()
