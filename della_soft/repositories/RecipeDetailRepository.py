"""RecipeDetailRepository
---------------------------------
Funciones CRUD a nivel módulo para los detalles de recetas.

Coincide con los nombres que usa `RecipeDetailService`:
    * select_by_recipe_id(recipe_id)
    * insert_recipe_detail(detail)
    * delete_recipe_detail(detail_id)

Además incluye utilidades extra:
    * delete_by_recipe(recipe_id)
    * update_recipe_detail(detail)  # opcional
    * select_all()

Cada función acepta un `session` opcional; si no se provee abre y cierra
su propia sesión usando `connect()`.
"""

from typing import List, Sequence, Dict, Any, Union

from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from ..models.RecipeDetailModel import RecipeDetail
from .ConnectDB import connect
# ---------------------------------------------------------------------------
# SELECT --------------------------------------------------------------------
# ---------------------------------------------------------------------------

def select_by_recipe_id(recipe_id: int, *, session: Session | None = None) -> List[RecipeDetail]:
    """Devuelve todos los detalles de una receta (eager‐load ingrediente)."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        stmt = (
            select(RecipeDetail)
            .where(RecipeDetail.id_recipe == recipe_id)
            .options(joinedload(RecipeDetail.ingredient))
        )
        return list(session.exec(stmt))
    finally:
        if own:
            session.close()


def select_all(*, session: Session | None = None) -> List[RecipeDetail]:
    """Devuelve todos los RecipeDetail – útil para debug."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        stmt = select(RecipeDetail).options(joinedload(RecipeDetail.ingredient))
        return list(session.exec(stmt))
    finally:
        if own:
            session.close()

# ---------------------------------------------------------------------------
# INSERT --------------------------------------------------------------------
# ---------------------------------------------------------------------------

def insert_recipe_detail(detail: Union[RecipeDetail, Dict[str, Any]], *, session: Session | None = None) -> RecipeDetail:
    """Inserta un único detalle y devuelve el objeto persistido con ID."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        if not isinstance(detail, RecipeDetail):
            detail = RecipeDetail(**detail)
        session.add(detail)
        session.commit()
        session.refresh(detail)
        return detail
    finally:
        if own:
            session.close()

# ---------------------------------------------------------------------------
# UPDATE --------------------------------------------------------------------
# ---------------------------------------------------------------------------

def update_recipe_detail(detail: RecipeDetail, *, session: Session | None = None) -> RecipeDetail:
    """Actualiza (merge) un detalle existente."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        detail = session.merge(detail)
        session.commit()
        session.refresh(detail)
        return detail
    finally:
        if own:
            session.close()

# ---------------------------------------------------------------------------
# DELETE --------------------------------------------------------------------
# ---------------------------------------------------------------------------

def delete_recipe_detail(detail_id: int, *, session: Session | None = None) -> None:
    """Elimina un RecipeDetail por su `id`."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        stmt = select(RecipeDetail).where(RecipeDetail.id == detail_id)
        detail = session.exec(stmt).one_or_none()
        if detail:
            session.delete(detail)
            session.commit()
    finally:
        if own:
            session.close()


def delete_by_recipe(recipe_id: int, *, session: Session | None = None) -> None:
    """Elimina todos los detalles asociados a una receta."""
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        session.exec(
            select(RecipeDetail).where(RecipeDetail.id_recipe == recipe_id)
        ).delete()
        session.commit()
    finally:
        if own:
            session.close()
