
from typing import List, Sequence, Dict, Any, Union

from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from ..models.RecipeModel import Recipe
from ..models.RecipeDetailModel import RecipeDetail
from .ConnectDB import connect  # Ajusta si está en otra ruta


# della_soft/repositories/RecipeRepository.py
from sqlmodel import select, Session
from sqlalchemy.orm import joinedload
from ..models.RecipeModel import Recipe
from ..models.RecipeDetailModel import RecipeDetail
from .ConnectDB import connect           # tu helper

# ---------------------------------------------------------------------------
# SELECT --------------------------------------------------------------------
# ---------------------------------------------------------------------------
def select_all(*, session: Session | None = None) -> list[Recipe]:
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)

    try:
        stmt = (
            select(Recipe)
            .options(
                joinedload(Recipe.recipe_detail)           #  tu relación
                .joinedload(RecipeDetail.ingredient)
            )
        )
        # ⚠️  evita duplicados y devuelve objetos Recipe
        return session.exec(stmt).unique().all()

    finally:
        if own:
            session.close()


def get_recipe(recipe_id: int, *, session: Session | None = None) -> Recipe | None:
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)

    try:
        stmt = (
            select(Recipe)
            .where(Recipe.id == recipe_id)
            .options(
                joinedload(Recipe.recipe_detail)
                .joinedload(RecipeDetail.ingredient)
            )
        )
        return session.exec(stmt).unique().all()


    finally:
        if own:
            session.close()


# ---------------------------------------------------------------------------
# INSERT --------------------------------------------------------------------
# ---------------------------------------------------------------------------

def insert_recipe(recipe: Recipe, *, session: Session | None = None) -> Recipe:
    """Inserta la receta y devuelve el objeto con su ID."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
        return recipe
    finally:
        if own:
            session.close()

# ---------------------------------------------------------------------------
# UPDATE --------------------------------------------------------------------
# ---------------------------------------------------------------------------

def update_recipe(recipe: Recipe, *, session: Session | None = None) -> Recipe:
    """Actualiza (merge) la receta y devuelve el objeto actualizado."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        recipe = session.merge(recipe)
        session.commit()
        session.refresh(recipe)
        return recipe
    finally:
        if own:
            session.close()

# ---------------------------------------------------------------------------
# DELETE --------------------------------------------------------------------
# ---------------------------------------------------------------------------

def delete_recipe(recipe_id: int, *, session: Session | None = None) -> None:
    """Elimina la receta y sus detalles en cascada (si la FK está configurada).
    Si no, elimina detalles manualmente antes de borrar la receta.
    """
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        stmt = select(Recipe).where(Recipe.id == recipe_id)
        rec = session.exec(stmt).one_or_none()
        if rec:
            # Si la FK no está en cascade, borramos detalles primero.
            for det in rec.details:
                session.delete(det)
            session.delete(rec)
            session.commit()
    finally:
        if own:
            session.close()

# ---------------------------------------------------------------------------
# HELPERS DE DETALLE ---------------------------------------------------------
# ---------------------------------------------------------------------------

def _prepare_detail(obj: Union[RecipeDetail, Dict[str, Any]], recipe_id: int) -> RecipeDetail:
    """Convierte dict a RecipeDetail y le asigna id_recipe."""
    if isinstance(obj, RecipeDetail):
        obj.id_recipe = recipe_id
        return obj
    return RecipeDetail(id_recipe=recipe_id, **obj)


def add_details(
    recipe_id: int,
    details: Sequence[Union[RecipeDetail, Dict[str, Any]]],
    *,
    session: Session | None = None,
) -> List[RecipeDetail]:
    """Inserta todos los detalles pasados; devuelve los objetos persistidos."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        persisted: list[RecipeDetail] = []
        for obj in details:
            det = _prepare_detail(obj, recipe_id)
            session.add(det)
            persisted.append(det)
        session.commit()
        for det in persisted:
            session.refresh(det)
        return persisted
    finally:
        if own:
            session.close()


from sqlalchemy import delete     # ← ponlo junto a los demás imports

def sync_details(
    recipe_id: int,
    new_details: Sequence[Union[RecipeDetail, Dict[str, Any]]],
    *,
    session: Session | None = None,
) -> List[RecipeDetail]:
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        
        stmt_del = delete(RecipeDetail).where(RecipeDetail.id_recipe == recipe_id)
        session.exec(stmt_del)
        session.commit()

        
        return add_details(recipe_id, new_details, session=session)
    finally:
        if own:
            session.close()
