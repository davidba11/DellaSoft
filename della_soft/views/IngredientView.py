import reflex as rx
from typing import List

from ..services.IngredientService import select_all_ingredient_service, select_ingredient_service, create_ingredient, update_ingredient_service

from ..services.MeasureService import select_name_by_id, select_all_measure_service

from ..models.IngredientModel import Ingredient

class IngredientView(rx.State):

    columns: List[str] = ["ID", "Ingrediente", "Medida", "Acciones"]

    data: List[dict] = []
    offset: int = 0
    limit: int = 5
    total_items: int = 0

    input_search: str

    measure_search = ""
    measure_dropdown_open = False
    selected_measure_label = ""
    selected_measure_id: int | None = None

    measure_options: List[str] = []
    _measure_map: dict[str, int]
    measure_ingredient_label = ""

    edit_modal_open: bool = False
    modal_ingredient: Ingredient | None = None
    create_modal_open: bool = False
    edit_modal_open: bool = False


    @rx.event
    async def open_edit_modal(self, ingredient_id: int):
        ingredient = next((o for o in await select_all_ingredient_service() if o.id == ingredient_id), None)
        if ingredient:
            await self.load_measures()
            self.modal_ingredient = ingredient
            self.selected_measure_id = ingredient.measure_id
            label = next(
                (lbl for lbl, mid in self._measure_map.items() if mid == ingredient.measure_id),
                ""
            )
            self.selected_measure_label = label
            self.measure_search = label
            self.edit_modal_open = True
            self.set()


    @rx.event
    def close_edit_modal(self):
        self.edit_modal_open = False
        self.modal_ingredient = None
        self.selected_measure_label = ""
        self.selected_measure_id = None
        self.measure_search = ""
        self.set()

    @rx.event
    def set_create_modal_open(self, value: bool):
        self.create_modal_open = value
        self.set()

    @rx.event
    async def update_ingredient_controller(self, form_data: dict):
        try:
            ingredient_id = int(form_data["id"])
            measure_id = int(form_data["id_measure"])
            name = form_data["name"].strip()
            updated_ingredient = Ingredient(id=ingredient_id, name=name, measure_id=measure_id)
            update_ingredient_service(updated_ingredient)
            yield rx.toast("Ingrediente actualizado correctamente.", duration=3000, position="bottom-right")
            yield IngredientView.close_edit_modal()    # <--- Cierra el modal de edición
            yield IngredientView.load_ingredients()
            self.set()
        except Exception as e:
            print("Error actualizando ingrediente:", e)
            yield rx.toast("Error al actualizar el ingrediente.", duration=3000, position="bottom-right", status="error")


    async def get_all_ingredients(self):
        ingredients = await select_all_ingredient_service()
        q = (self.input_search or "").lower()

        resultados = []
        for o in ingredients:
            medida = select_name_by_id(o.measure_id) or ""
            campos = [str(o.id), o.name, medida]
            if any(q in campo.lower() for campo in campos):
                resultados.append({"id": o.id, "name": o.name, "medida": medida})

        # paginación
        self.total_items = len(resultados)
        paginados = resultados[self.offset : self.offset + self.limit]

        self.data = paginados                # ✅ actualiza el estado
        self.set()
        return paginados

    @rx.event
    async def load_ingredients(self):
        await self.get_all_ingredients()

    async def get_ingredient(self):
        ingredientes = await select_ingredient_service(self.input_search)

        resultados = []
        for o in ingredientes:
            medida = select_name_by_id(o.measure_id) or ""
            resultados.append({"id": o.id, "name": o.name, "medida": medida})

        self.total_items = len(resultados)
        self.offset = 0
        self.data = resultados[self.offset : self.offset + self.limit]
        self.set()

    @rx.event
    async def load_ingredient_information(self, value: str):
        self.input_search = value
        await self.get_ingredient()

    @rx.event
    def on_measure_search(self, value: str):
        self.measure_search = value or ""
        self.measure_dropdown_open = True
        self.set()

    @rx.var
    def filtered_measure_options(self) -> List[str]:
        if not self.measure_search:
            return self.measure_options
        txt = self.measure_search.lower()
        return [opt for opt in self.measure_options if txt in opt.lower()]
    
    @rx.event
    def select_measure(self, label: str):
        self.selected_measure_label = label
        self.selected_measure_id = self._measure_map[label]
        self.measure_search = label
        self.measure_dropdown_open = False
        self.set()

    @rx.event
    async def prev_page(self):
        """Vuelve a la página anterior."""
        if self.offset > 0:
            self.offset -= self.limit
            await self.load_ingredients()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1
    
    @rx.event
    async def next_page(self):
        """Pasa a la siguiente página si hay más productos."""
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_ingredients()

    @rx.event
    async def load_measures(self):
        measures = await select_all_measure_service()
        opts, mmap = [], {}
        for m in measures:
            label = f"({m.description})"
            opts.append(label)
            mmap[label] = m.id
        self.measure_options = opts
        self._measure_map = mmap
        self.measure_search = ""
        self.selected_measure_label = ""
        self.measure_dropdown_open = False
        self.set()

    @rx.event
    async def insert_ingredient_controller(self, form_data: dict):
        try:
            medida_id = int(form_data["id_measure"])
            create_ingredient(id="", name=form_data['name'], measure_id=medida_id)
            yield rx.toast("Ingrediente creado correctamente.", duration=3000, position="bottom-right")
            yield IngredientView.set_create_modal_open(False)   # <--- Cierra el modal de creación
            yield IngredientView.load_ingredients()
            self.set()
        except BaseException as e:
            print(e.args)
            yield rx.toast("Error al crear el ingrediente.", duration=3000, position="bottom-right", status="error")
            raise
   
    @rx.var
    def selected_measure_str(self) -> str:
        """Devuelve el id como string o vacío si aún no hay selección."""
        return "" if self.selected_measure_id is None else str(self.selected_measure_id)

def get_title():
    return rx.text(
        "Ingredientes",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="80%",
    )

def search_ingredient_component () ->rx.Component:
    return rx.hstack(
        rx.input(
            placeholder='Buscar Ingrediente',
            background_color="#3E2723", 
            placeholder_color="white", 
            color="white",
            on_change=IngredientView.load_ingredient_information,
        ),
    ),

def create_ingredient_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.grid(
                rx.text("Ingrediente:", color="white"),
                rx.input(
                    placeholder="Ingrediente",
                    name="name",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                rx.text("Medida:", color="white"),
                rx.vstack(
                    rx.box(
                        rx.input(
                            placeholder="Buscar Medida...",
                            background_color="#5D4037",
                            color="white",
                            value=IngredientView.measure_search,
                            on_change=IngredientView.on_measure_search,
                        ),
                        rx.cond(
                            IngredientView.measure_dropdown_open,
                            rx.vstack(
                                rx.foreach(
                                    IngredientView.filtered_measure_options,
                                    lambda label: rx.box(
                                        rx.text(label, text_align="center", color="#3E2723"),
                                        on_click=lambda label=label: IngredientView.select_measure(label),
                                        style={
                                            "padding": "0.5rem",
                                            "cursor": "pointer",
                                            "_hover": {"background_color": "#A67B5B", "color": "white"},
                                        },
                                    ),
                                ),
                                background_color="#FFF8E1",
                                border="1px solid #A67B5B",
                                border_radius="0 0 8px 8px",
                                max_height="160px",
                                overflow_y="auto",
                                style={
                                    "position": "absolute",
                                    "top": "100%",
                                    "left": 0,
                                    "right": 0,
                                    "z_index": 1000,
                                },
                            ),
                        ),
                        style={"position": "relative", "width": "100%"},
                    ),
                    rx.input(
                        name="id_measure",
                        type="hidden",
                        value=IngredientView.selected_measure_str,
                    ),
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.button(
    rx.icon("save", size=22),            # ← AQUÍ el texto, sin children=
    type="submit",
    background_color="#3E2723",
    color="white",
    size="2",
    variant="solid",
        ),
        ),
        on_submit=IngredientView.insert_ingredient_controller,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True,
        align="center",
        justify="center",
    )

def create_ingredient_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                # Abre el modal y carga las medidas
                on_click=lambda: [
                    IngredientView.load_measures(),
                    IngredientView.set_create_modal_open(True)
                ],
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Crear Ingrediente'),
                create_ingredient_form(),
                justify='center',
                align='center',
                direction='column',
                weight="bold"
            ),
            background_color="#A67B5B",
        ),
        open=IngredientView.create_modal_open,
        on_open_change=IngredientView.set_create_modal_open,
        style={"width": "300px"}
    )

def edit_ingredient_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="id",
                type="hidden",
                value=rx.cond(
                    IngredientView.modal_ingredient,
                    IngredientView.modal_ingredient.id,
                    ""
                ),
            ),
            rx.grid(
                rx.text("Ingrediente:", color="white"),
                rx.input(
                    placeholder="Ingrediente",
                    name="name",
                    background_color="#3E2723",
                    color="white",
                    width="100%",
                    default_value=rx.cond(
                        IngredientView.modal_ingredient,
                        IngredientView.modal_ingredient.name,
                        ""
                    ),
                ),
                rx.text("Medida:", color="white"),
                rx.vstack(
                    rx.box(
                        rx.input(
                            placeholder="Buscar Medida...",
                            background_color="#5D4037",
                            color="white",
                            value=IngredientView.measure_search,
                            on_change=IngredientView.on_measure_search,
                        ),
                        rx.cond(
                            IngredientView.measure_dropdown_open,
                            rx.vstack(
                                rx.foreach(
                                    IngredientView.filtered_measure_options,
                                    lambda label: rx.box(
                                        rx.text(label, text_align="center", color="#3E2723"),
                                        on_click=lambda label=label: IngredientView.select_measure(label),
                                        style={
                                            "padding": "0.5rem",
                                            "cursor": "pointer",
                                            "_hover": {"background_color": "#A67B5B", "color": "white"},
                                        },
                                    ),
                                ),
                                background_color="#FFF8E1",
                                border="1px solid #A67B5B",
                                border_radius="0 0 8px 8px",
                                max_height="160px",
                                overflow_y="auto",
                                style={
                                    "position": "absolute",
                                    "top": "100%",
                                    "left": 0,
                                    "right": 0,
                                    "z_index": 1000,
                                },
                            ),
                        ),
                        style={"position": "relative", "width": "100%"},
                    ),
                    rx.input(
                        name="id_measure",
                        type="hidden",
                        value=IngredientView.selected_measure_str,
                    ),
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.dialog.close(
                rx.button(
                    rx.icon("save", size=22), 
                    type="submit",
                    background_color="#3E2723",
                    color="white",
                    size="2",
                    variant="solid",
                )
            ),
            spacing="3",
        ),
        on_submit=IngredientView.update_ingredient_controller,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True,
        align="center",
        justify="center",
    )


def edit_ingredient_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Editar Ingrediente'),
                edit_ingredient_form(),
                justify='center',
                align='center',
                direction='column',
                weight="bold"
            ),
            background_color="#A67B5B",
        ),
        open=IngredientView.edit_modal_open,
        on_open_change=IngredientView.close_edit_modal,
        style={"width": "300px"}
    )


def main_actions_form():
    return rx.hstack(
        search_ingredient_component(), 
        create_ingredient_modal(),
        justify='center',
        style={"margin-top": "auto"}
    ),

def get_table_header():
    return rx.table.row(
        rx.table.column_header_cell(IngredientView.columns[0]),
        rx.table.column_header_cell(IngredientView.columns[1]),
        rx.table.column_header_cell(IngredientView.columns[2]),
        rx.table.column_header_cell(IngredientView.columns[3]),
        color="#3E2723",
        background_color="#A67B5B",
    ),

def get_table_body(ingredient: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(ingredient["id"])),
        rx.table.cell(rx.text(ingredient["name"])),
        rx.table.cell(rx.text(ingredient["medida"])),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("square-pen", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    on_click=lambda: IngredientView.open_edit_modal(ingredient["id"]),
                ),
                spacing="2",
            )
        ),
        color="#3E2723",
    )

def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
            on_click=IngredientView.prev_page,
            is_disabled=IngredientView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        rx.text(  
            IngredientView.current_page, " de ", IngredientView.num_total_pages
        ),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=IngredientView.next_page,
            is_disabled=IngredientView.offset + IngredientView.limit >= IngredientView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        justify="center",
        color="#3E2723",
    )

def ingredients() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_form(),
            edit_ingredient_modal(),   # <-- Aquí lo agregas
            rx.table.root(
                rx.table.header(
                    get_table_header(),
                ),
                rx.table.body(
                    rx.foreach(IngredientView.data, get_table_body)
                ),
                width="80vw",
                background_color="#FFF8E1",
                border_radius="20px",
            ),
            pagination_controls(),
            spacing="5",
            align="center",
            width="80vw",
        ),
        display="flex",
        justifyContent="center",
        alignItems="flex-start",
        text_align="center",
        background_color="#FDEFEA",
        width="92vw",
        height="80vh",
    )
