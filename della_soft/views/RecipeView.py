import reflex as rx
from typing import List, Dict, Optional

from della_soft.repositories.LoginRepository import AuthState
from della_soft.repositories.ProductRepository import get_product

from .ProductView import ProductView, get_table_header as product_table_header
from ..services.ProductService import select_all_product_service
from ..services.RecipeService import (
    select_all_recipe_service,
    insert_recipe_service,
    update_recipe_service,
    select_recipe_detail_by_recipe_id_service,
)
from ..services.IngredientService import select_all_ingredient_service
from ..models.ProductModel import Product
from ..models.RecipeModel import Recipe
from ..models.RecipeDetailModel import RecipeDetail

class RecipeView(ProductView):
    """Pantalla de gestión de Recetas."""

    recipe_map: Dict[int, Recipe] = {}

    create_modal_open: bool = False
    edit_modal_open: bool = False

    selected_product: Optional[Product] = None
    selected_recipe: Optional[Recipe] = None

    form_description: str = ""
    ingredient_rows: List[Dict[str, Optional[int]]] = []

    _ingredient_options: List[str] = []
    _ingredient_map: Dict[str, int] = {}

    # Para el modal de ver receta
    view_modal_open: bool = False
    view_product_name: str = ""
    view_description: str = ""
    _view_ingredient_rows: list = []
    recipe_input_search: str = ""

    # -------------------------- Vars reactivas --------------------------------
    @rx.var
    def ingredient_options(self) -> List[str]:
        return self._ingredient_options

    @rx.var
    def modal_title(self) -> str:
        return "Crear Receta" if self.selected_recipe is None else "Editar Receta"

    @rx.var
    def product_label(self) -> str:
        return f"Producto: {self.selected_product.name}" if self.selected_product else "Producto: —"

    @rx.var
    def ingredient_row_indices(self) -> List[int]:
        return list(range(len(self.ingredient_rows)))
    
    @rx.var
    def recipe_product_ids(self) -> set:
        return set(self.recipe_map.keys())

    @rx.var
    def ingredient_rows_labels(self) -> List[str]:
        labels: list[str] = []
        invert = {v: k for k, v in self._ingredient_map.items()}
        for row in self.ingredient_rows:
            lbl = invert.get(row.get("ingredient_id"), "")
            labels.append(lbl)
        return labels

    @rx.var
    def ingredient_rows_quantities(self) -> List[str]:
        return [str(row["quantity"]) if row.get("quantity") is not None else "" for row in self.ingredient_rows]

    @rx.var
    def disable_prev(self) -> bool:
        return self.offset <= 0

    @rx.var
    def disable_next(self) -> bool:
        return self.offset + self.limit >= self.total_items

    @rx.var
    def page_info(self) -> str:
        return f"{self.current_page} de {self.num_total_pages}"

    @rx.var
    def is_modal_open(self) -> bool:
        return self.create_modal_open or self.edit_modal_open

    # --- Vars para el modal de ver receta ---
    @rx.var
    def view_ingredient_rows(self) -> List[dict]:
        # Esto será una lista de dicts con label y quantity como STR
        return self._view_ingredient_rows

    # Diccionario: {product_id: True} si tiene receta
    @rx.var
    def product_has_recipe(self) -> dict:
        return {pid: True for pid in self.recipe_map}

    # -------------------------- Eventos simples -------------------------------
    @rx.event
    def set_description(self, value: str):
        self.form_description = value
        self.set()

    # -------------------------- Carga inicial ---------------------------------
    @rx.event
    async def load_products_and_recipes(self):
        products = await select_all_product_service()
        self.total_items = len(products)
        self.data = products[self.offset : self.offset + self.limit]

        recipes = await select_all_recipe_service()
        self.recipe_map = {r.id_product: r for r in recipes}

        ingredients = await select_all_ingredient_service()
        opts, mp = [], {}
        for ing in ingredients:
            unit = getattr(ing.measure, "description", "")
            label = f"{ing.name} ({unit})" if unit else ing.name
            opts.append(label)
            mp[label] = ing.id
        self._ingredient_options = opts
        self._ingredient_map = mp
        self.set()

    # -------------------------- Paginación ------------------------------------
    async def next_page(self):
        if not self.disable_next:
            self.offset += self.limit
            await self.load_products_and_recipes()

    async def prev_page(self):
        if not self.disable_prev:
            self.offset -= self.limit
            await self.load_products_and_recipes()

    # -------------------------- Modal helpers ---------------------------------
    @rx.event
    def open_create_modal(self, product: Product):
        self.selected_product = product
        self.selected_recipe = None
        self.form_description = ""
        self.ingredient_rows = [{"ingredient_id": None, "quantity": None}]
        self.create_modal_open = True
        self.set()

    @rx.event
    async def open_edit_modal(self, product: Product):
        recipe = self.recipe_map.get(product.id)
        if not recipe:
            return
        self.selected_product = product
        self.selected_recipe = recipe
        self.form_description = recipe.description
        details = await select_recipe_detail_by_recipe_id_service(recipe.id)
        self.ingredient_rows = [
            {"ingredient_id": d.id_ingredient, "quantity": d.quantity} for d in details
        ] or [{"ingredient_id": None, "quantity": None}]
        self.edit_modal_open = True
        self.set()

    # Modal de vista solo lectura
    @rx.event
    async def open_view_modal(self, product: Product):
        recipe = self.recipe_map.get(product.id)
        if not recipe:
            return
        self.view_product_name = product.name
        self.view_description = recipe.description
        details = await select_recipe_detail_by_recipe_id_service(recipe.id)
        invert = {v: k for k, v in self._ingredient_map.items()}
        self._view_ingredient_rows = [
            {
                "label": invert.get(d.id_ingredient, ""),
                "quantity": str(d.quantity) if d.quantity is not None else "",
            }
            for d in details
        ]
        self.view_modal_open = True
        self.set()

    @rx.event
    def set_view_modal_open_flag(self, is_open: bool):
        self.view_modal_open = is_open
        self.set()

    @rx.event
    def set_modal_open_flag(self, is_open: bool):
        if not is_open:
            self.create_modal_open = False
            self.edit_modal_open = False
            self.set()

    # -------------------------- Filas dinámicas -------------------------------
    @rx.event
    def add_ingredient_row(self):
        self.ingredient_rows.append({"ingredient_id": None, "quantity": None})
        self.set()

    @rx.event
    def remove_ingredient_row(self, index: int):
        if len(self.ingredient_rows) > 1:
            self.ingredient_rows.pop(index)
            self.set()

    @rx.event
    def update_ingredient(self, index: int, label: str):
        ing_id = self._ingredient_map.get(label)
        self.ingredient_rows[index]["ingredient_id"] = ing_id
        self.set()

    @rx.event
    def update_quantity(self, index: int, value: str):
        txt = value.replace(",", ".").strip()
        if txt == "":
            qty = None
        else:
            try:
                qty = float(txt)
            except ValueError:
                qty = None
        self.ingredient_rows[index]["quantity"] = qty
        self.set()

    # -------------------------- Persistencia ----------------------------------
    @rx.event
    def submit_form(self, form_data: dict):
        if self.selected_recipe is None:
            yield from self.insert_recipe_controller(form_data)
        else:
            yield from self.update_recipe_controller(form_data)

    @rx.event
    def insert_recipe_controller(self, form_data: dict):
        new_recipe = Recipe(
            id=None,
            id_product=self.selected_product.id,
            description=form_data.get("description", ""),
        )
        created = insert_recipe_service(new_recipe)

        details = [
            RecipeDetail(id=None, id_recipe=created.id, id_ingredient=row["ingredient_id"], quantity=row["quantity"])
            for row in self.ingredient_rows
            if row["ingredient_id"] and row["quantity"]
        ]
        if details:
            insert_recipe_service.add_details(created.id, details)

        yield rx.toast("Receta creada con éxito")
        self.create_modal_open = False
        yield RecipeView.load_products_and_recipes()

    @rx.event
    def update_recipe_controller(self, form_data: dict):
        if not self.selected_recipe:
            return
        self.selected_recipe.description = form_data.get("description", "")
        update_recipe_service(self.selected_recipe)

        details = [
            RecipeDetail(id=None, id_recipe=self.selected_recipe.id, id_ingredient=row["ingredient_id"], quantity=row["quantity"])
            for row in self.ingredient_rows
            if row["ingredient_id"] and row["quantity"]
        ]
        update_recipe_service.sync_details(self.selected_recipe.id, details)

        yield rx.toast("Receta actualizada con éxito")
        self.edit_modal_open = False
        yield RecipeView.load_products_and_recipes()

    # -------------------------- Acción botón Receta --------------------------
    @rx.event
    async def handle_recipe_click(self, prod_id: int):
        prod = next((p for p in self.data if p.id == prod_id), None)
        if not prod:
            return
        if self.recipe_map.get(prod_id):
            await self.open_edit_modal(prod)
        else:
            self.open_create_modal(prod)

    # Acción botón de ver
    @rx.event
    async def handle_view_recipe(self, prod_id: int):
        prod = next((p for p in self.data if p.id == prod_id), None)
        if not prod:
            return
        await self.open_view_modal(prod)

    async def get_product(self):
        self.data = await get_product(self.recipe_input_search)
        self.total_items = len(self.data) 
        self.offset = 0 
        self.data = self.data[self.offset : self.offset + self.limit]  
        self.set()
    
    async def load_product_information(self, value: str):
        self.recipe_input_search = value
        await self.get_product()

def ingredient_row_component(idx: int):
    return rx.hstack(
        rx.select(
            items=RecipeView.ingredient_options,
            placeholder="Ingrediente",
            value=RecipeView.ingredient_rows_labels[idx],
            on_change=lambda lbl, i=idx: RecipeView.update_ingredient(i, lbl),
            width="60%",
            background_color="#3E2723",
            color="white",
        ),
        rx.input(
            placeholder="Cantidad",
            value=RecipeView.ingredient_rows_quantities[idx],
            on_change=lambda v, i=idx: RecipeView.update_quantity(i, v),
            width="30%",
            background_color="#3E2723",
            color="white",
        ),
        rx.icon(
            "x",
            size=20,
            color="#3E2723",
            on_click=lambda i=idx: RecipeView.remove_ingredient_row(i),
        ),
        spacing="2",
        justify="center",
    )

def create_recipe_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.text(RecipeView.product_label, weight="bold", color="#3E2723"),
            rx.text_area(
                name="description",
                placeholder="Descripción de la receta",
                background_color="#3E2723",
                color="white",
                on_change=RecipeView.set_description,
                value=RecipeView.form_description,
                width="100%",
                rows="3",
            ),
            rx.divider(),
            rx.text("Ingredientes", weight="bold", color="#3E2723"),
            rx.vstack(
                rx.foreach(RecipeView.ingredient_row_indices, ingredient_row_component),
                spacing="3",
                width="100%",
            ),
            rx.button(
                rx.icon("plus", size=22),
                type="button",
                on_click=RecipeView.add_ingredient_row,
                background_color="#3E2723",
            ),
            rx.divider(),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        rx.icon("save", size=22),
                        type="submit",
                        background_color="#3E2723",
                        color="white",
                        size="2",
                        variant="solid",
                    ),
                ),
                spacing="3",
            ),
            spacing="4",
            width="100%",
            align="center",
        ),
        on_submit=RecipeView.submit_form,
        debug=True,
        width="100%",
    )

def create_recipe_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.flex(
                rx.dialog.title(RecipeView.modal_title),
                create_recipe_form(),
                direction="column",
                align="center",
                justify="center",
                gap="3",
            ),
            background_color="#A67B5B",
            style={"max_width": "600px", "max_height": "600px"},
            padding="3",
        ),
        open=RecipeView.is_modal_open,
        on_open_change=RecipeView.set_modal_open_flag,  # Se cierra al hacer click fuera
    )

def view_recipe_modal():
    return rx.dialog.root(
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Ver Receta"),
                rx.text(f"Producto: {RecipeView.view_product_name}", weight="bold", color="#3E2723"),
                rx.text(f"Descripción: {RecipeView.view_description}", color="#3E2723"),
                rx.text("Ingredientes:", weight="bold", color="#3E2723"),
                rx.vstack(
                    rx.foreach(
                        RecipeView.view_ingredient_rows,
                        lambda row: rx.hstack(
                            rx.text(row["label"], color="#3E2723", width="60%"),
                            rx.text(row["quantity"], color="#3E2723", width="30%"),
                        ),
                    ),
                    spacing="2",
                ),
                direction="column",
                align="center",
                justify="center",
                gap="3",
            ),
            background_color="#A67B5B",
            style={"max_width": "600px", "max_height": "600px"},
            padding="3",
        ),
        open=RecipeView.view_modal_open,
        on_open_change=RecipeView.set_view_modal_open_flag,
    )

def search_product_component () ->rx.Component:
    return rx.hstack(
        rx.input(
            placeholder='Buscar Producto',
            background_color="#3E2723", 
            placeholder_color="white", 
            color="white",
            on_change=RecipeView.load_product_information,
        ),
    )

def get_table_body(product: Product):
    return rx.table.row(
        rx.table.cell(product.name),
        rx.table.cell(product.description),
        rx.table.cell(product.product_type),
        rx.table.cell(product.price),
        rx.table.cell(
            rx.cond(
                AuthState.is_admin,
                rx.button(
                    rx.icon("square-pen", size=20),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    on_click=lambda pid=product.id: RecipeView.handle_recipe_click(pid),
                ),
                None
            ),
            rx.cond(
                RecipeView.recipe_product_ids.contains(product.id),
                rx.button(
                    rx.icon("eye", size=20),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    ml="2",
                    on_click=lambda pid=product.id: RecipeView.handle_view_recipe(pid),
                ),
                None
            ),
        ),
        color="#3E2723",
    )

@rx.page()
def recipes() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Recetas de Productos", size="7", weight="bold", color="#3E2723"),
            create_recipe_modal(),
            view_recipe_modal(),
            search_product_component(),
            rx.table.root(
                rx.table.header(product_table_header()),
                rx.table.body(rx.foreach(RecipeView.data, get_table_body)),
                width="90%",
                background_color="#FFF8E1",
                border_radius="20px",
            ),
            rx.hstack(
                rx.button(
                    rx.icon("arrow-left", size=22),
                    on_click=RecipeView.prev_page,
                    is_disabled=RecipeView.disable_prev,
                    background_color="#3E2723",
                    size="2",
                ),
                rx.text(RecipeView.page_info),
                rx.button(
                    rx.icon("arrow-right", size=22),
                    on_click=RecipeView.next_page,
                    is_disabled=RecipeView.disable_next,
                    background_color="#3E2723",
                    size="2",
                ),
                justify="center",
            ),
            spacing="5",
            align="center",
            width="100%",
        ),
        display="flex",
        flex_direction="column",
        align_items="center",
        justify_content="flex-start",
        width="100%",
        padding="2rem",
        background_color="#FDEFEA",
        on_mount=RecipeView.load_products_and_recipes,
    )
