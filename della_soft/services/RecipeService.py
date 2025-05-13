
from typing import List

from ..repositories import RecipeRepository as recipe_repo
from ..repositories import RecipeDetailRepository as detail_repo
from ..models.RecipeModel import Recipe
from ..models.RecipeDetailModel import RecipeDetail

# ---------------------------------------------------------------------------
#  Recetas -------------------------------------------------------------------
# ---------------------------------------------------------------------------

async def select_all_recipe_service() -> List[Recipe]:
    """Devuelve todas las recetas con sus detalles."""
    return recipe_repo.select_all()

# Alias directos (sincronos) – se usan como funciones pero luego les añadimos helpers
insert_recipe_service = recipe_repo.insert_recipe
update_recipe_service = recipe_repo.update_recipe

# Helpers de detalle (añadidos como atributos para compatibilidad con la vista)
insert_recipe_service.add_details = recipe_repo.add_details
update_recipe_service.sync_details = recipe_repo.sync_details

# ---------------------------------------------------------------------------
#  Detalles de receta --------------------------------------------------------
# ---------------------------------------------------------------------------

async def select_recipe_detail_by_recipe_id_service(recipe_id: int) -> List[RecipeDetail]:
    """Devuelve los detalles de una receta (ingredientes + cantidades)."""
    return detail_repo.select_by_recipe_id(recipe_id)
