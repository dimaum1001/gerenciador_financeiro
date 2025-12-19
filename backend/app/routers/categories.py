from typing import List, Optional, Dict, Tuple
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.deps import get_current_user, get_current_non_demo_user, get_db
from app.models.user import User
from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from app.utils.locale_mapper import category_type_mapper

router = APIRouter()


def _category_query(db: Session, current_user: User):
    return db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.is_demo_data.is_(current_user.is_demo),
    )


def _build_category_meta(categories: List[Category]) -> Dict[UUID, Tuple[str, int, bool, str]]:
    categories_by_id = {category.id: category for category in categories}
    children_count: Dict[UUID, int] = {}

    for category in categories:
        if category.parent_id:
            children_count[category.parent_id] = children_count.get(category.parent_id, 0) + 1

    full_name_cache: Dict[UUID, str] = {}
    level_cache: Dict[UUID, int] = {}
    visiting: set[UUID] = set()

    def compute_full_name(category_id: UUID) -> str:
        cached = full_name_cache.get(category_id)
        if cached is not None:
            return cached

        category = categories_by_id.get(category_id)
        if not category:
            return ""

        if category_id in visiting:
            return category.nome

        visiting.add(category_id)
        if category.parent_id and category.parent_id in categories_by_id:
            parent_name = compute_full_name(category.parent_id)
            full_name = f"{parent_name} > {category.nome}" if parent_name else category.nome
        else:
            full_name = category.nome
        visiting.discard(category_id)

        full_name_cache[category_id] = full_name
        return full_name

    def compute_level(category_id: UUID) -> int:
        cached = level_cache.get(category_id)
        if cached is not None:
            return cached

        category = categories_by_id.get(category_id)
        if not category:
            return 0

        if category_id in visiting:
            return 0

        visiting.add(category_id)
        if category.parent_id and category.parent_id in categories_by_id:
            level = compute_level(category.parent_id) + 1
        else:
            level = 0
        visiting.discard(category_id)

        level_cache[category_id] = level
        return level

    def tipo_display(tipo: CategoryType) -> str:
        return "Receita" if tipo == CategoryType.INCOME else "Despesa"

    meta: Dict[UUID, Tuple[str, int, bool, str]] = {}
    for category in categories:
        meta[category.id] = (
            compute_full_name(category.id),
            compute_level(category.id),
            children_count.get(category.id, 0) > 0,
            tipo_display(category.tipo),
        )

    return meta

@router.get("", include_in_schema=False, response_model=CategoryListResponse)
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
    categories = _category_query(db, current_user).all()
    meta_by_id = _build_category_meta(categories)

    # Aplicar filtros em memória para reduzir round-trips ao banco (DB remoto)
    filtered = categories

    if tipo:
        try:
            tipo_enum = category_type_mapper.to_enum(tipo)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de categoria inválido",
            )
        filtered = [category for category in filtered if category.tipo == tipo_enum]

    if parent_id is None:
        # Se não especificado, mostrar apenas categorias raiz
        filtered = [category for category in filtered if category.parent_id is None]
    elif parent_id != "":
        try:
            parent_uuid = UUID(parent_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="parent_id inválido",
            )
        filtered = [category for category in filtered if category.parent_id == parent_uuid]

    if ativo is not None:
        filtered = [category for category in filtered if category.ativo == ativo]

    if search:
        needle = search.casefold()

        def match(category: Category) -> bool:
            return (
                needle in (category.nome or "").casefold()
                or needle in (category.descricao or "").casefold()
            )

        filtered = [category for category in filtered if match(category)]

    filtered.sort(key=lambda category: (category.nome or "").casefold())
    total = len(filtered)

    paginated = filtered[skip : skip + limit]
    response_items: List[CategoryResponse] = []
    for category in paginated:
        nome_completo, nivel, is_parent, tipo_display = meta_by_id.get(
            category.id,
            (category.nome, 0, False, "Receita" if category.tipo == CategoryType.INCOME else "Despesa"),
        )
        response_items.append(
            CategoryResponse(
                id=category.id,
                user_id=category.user_id,
                nome=category.nome,
                tipo=category.tipo,
                parent_id=category.parent_id,
                cor=category.cor,
                icone=category.icone,
                descricao=category.descricao,
                ativo=category.ativo,
                incluir_relatorios=category.incluir_relatorios,
                meta_mensal=category.meta_mensal,
                nome_completo=nome_completo,
                nivel=nivel,
                is_parent=is_parent,
                tipo_display=tipo_display,
                criado_em=category.criado_em,
                atualizado_em=category.atualizado_em,
            )
        )

    return CategoryListResponse(
        categories=response_items,
        total=total,
        skip=skip,
        limit=limit,
    )

@router.post("", include_in_schema=False, response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
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
        tipo_enum = category_type_mapper.to_enum(tipo)
    except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo deve ser 'receita' ou 'despesa' (aceita também income/expense).",
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
