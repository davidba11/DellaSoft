
from typing import List, Sequence, Dict, Any, Union

from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from ..models.RecipeModel import Recipe
from ..models.RecipeDetailModel import RecipeDetail
from .ConnectDB import connect  

from sqlmodel import select, Session
from sqlalchemy.orm import joinedload
from ..models.RecipeModel import Recipe
from ..models.RecipeDetailModel import RecipeDetail
from .ConnectDB import connect     


def select_all(*, session: Session | None = None) -> list[Recipe]:
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)

    try:
        stmt = (
            select(Recipe)
            .options(
                joinedload(Recipe.recipe_details)           
                .joinedload(RecipeDetail.ingredient)
            )
        )

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


def insert_recipe(recipe: Recipe, *, session: Session | None = None) -> Recipe:

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


def update_recipe(recipe: Recipe, *, session: Session | None = None) -> Recipe:
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


def delete_recipe(recipe_id: int, *, session: Session | None = None) -> None:

    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        stmt = select(Recipe).where(Recipe.id == recipe_id)
        rec = session.exec(stmt).one_or_none()
        if rec:
            for det in rec.details:
                session.delete(det)
            session.delete(rec)
            session.commit()
    finally:
        if own:
            session.close()


def _prepare_detail(obj: Union[RecipeDetail, Dict[str, Any]], recipe_id: int) -> RecipeDetail:
    
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


from sqlalchemy import delete

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
