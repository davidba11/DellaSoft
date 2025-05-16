from della_soft.repositories import RecipeDetailRepository as repo
from della_soft.services import RecipeService

class RecipeDetailService:

    def get_by_recipe(self, recipe_id):
        return repo.select_by_recipe_id(recipe_id)

    def create_many(self, recipe_id, details):
        for d in details:
            d.id_recipe = recipe_id
            repo.insert_recipe_detail(d)

    def delete_one(self, detail_id):
        repo.delete_recipe_detail(detail_id)

    def get_recipe_with_details(self, recipe_id):
        recipe = RecipeService.get_recipe(recipe_id)
        details = self.get_by_recipe(recipe_id)
        return {"recipe": recipe, "details": details}
