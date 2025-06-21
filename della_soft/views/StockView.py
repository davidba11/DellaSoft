# della_soft/views/StockView.py
import reflex as rx
from typing import List

# ─── Servicios ──────────────────────────────────────────────────────────
from ..services.IngredientService      import select_all_ingredient_service
from ..services.IngredientStockService import (
    select_all_stock_service   as select_all_ing_stock_service,
    insert_ingredient_stock_service,
    update_ingredient_stock_service,
)
from ..services.ProductService         import select_all_product_service
from ..services.ProductStockService    import (
    select_all_stock_service   as select_all_prod_stock_service,
    insert_product_stock_service,
    update_product_stock_service,
)
from ..models.ProductModel             import ProductType
from ..services.MeasureService         import select_name_by_id
from ..repositories.LoginRepository import AuthState


class StockView(rx.State):

    @rx.event
    def change_edit_quantity(self, v: str):
        self.edit_quantity = float(v or 0)

    @rx.event
    def change_edit_min_quantity(self, v: str):
        self.edit_min_quantity = float(v or 0)

    # ─────────────────────────── constantes ────────────────────────────
    type_options: list[str] = ["Producto", "Ingrediente"]

    # pestaña activa
    selected_tab: str = "product"

    # columnas
    prod_columns = ["Producto", "Cantidad", "Mínimo", "Acciones"]
    ing_columns  = ["Ingrediente", "Cantidad", "Mínimo", "Medida", "Acciones"]

    # datos tabla
    product_rows:    list[dict] = []
    ingredient_rows: list[dict] = []

    # paginación / búsqueda
    offset = 0
    limit  = 5
    total_items = 0
    _page_data: list[dict] = []
    search_text = ""

    # ───────────────────────── Modal alta ────────────────────────────
    stock_type      = "Ingrediente"
    quantity: float = 0
    min_quantity: float = 0
    base_search = ""
    base_dropdown_open = False
    selected_base_label = ""
    selected_base_id: int | None = None
    base_options: List[str] = []
    _base_map: dict[str, str] = {}

    # ───────────────────────── Modal edición ──────────────────────────
    edit_modal_open          = False
    edit_stock_id:  int | None = None
    edit_stock_type          = ""
    edit_base_label          = ""
    edit_quantity:     float = 0
    edit_min_quantity: float = 0

    # ═══════════════════════ TABLA / BÚSQUEDA ════════════════════════
    @rx.event
    async def set_tab(self, tab: str):
        self.selected_tab = tab
        self.offset = 0
        await self.load_stock()

    @rx.event
    async def on_search(self, value: str):
        self.search_text = value or ""
        self.offset = 0
        await self.load_stock()

    @rx.event
    async def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_stock()

    @rx.event
    async def prev_page(self):
        if self.offset > 0:
            self.offset -= self.limit
            await self.load_stock()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items+self.limit-1)//self.limit,1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset//self.limit)+1

    @rx.var
    def page_rows(self) -> list[dict]:
        return self._page_data

    # ------------------------------------------------------------------
        
    async def _product_rows(self, filtro: str) -> list[dict]:
        stocks     = await select_all_prod_stock_service()
        productos  = {p.id: p for p in select_all_product_service()}

        return [
            {
                "stock_id":  ps.id,
                "id":        prod.id,
                "name":      prod.name,
                "qty":       ps.quantity,
                "min":       ps.min_quantity,
                "color":     stock_color(ps.quantity, ps.min_quantity),
            }
            for ps in stocks
            if (prod := productos.get(ps.product_id))               # existe el prod
            if not filtro or filtro in prod.name.lower()            # pasa filtro
        ]

    async def _ingredient_rows(self, filtro: str) -> list[dict]:
        stocks      = await select_all_ing_stock_service()
        ingredientes = {i.id: i for i in await select_all_ingredient_service()}

        return [
            {
                "stock_id":  is_.id,
                "id":        ing.id,
                "name":      ing.name,
                "qty":       is_.quantity,
                "min":       is_.min_quantity,
                "measure":   select_name_by_id(ing.measure_id),
                "color":     stock_color(is_.quantity, is_.min_quantity),
            }
            for is_ in stocks
            if (ing := ingredientes.get(is_.ingredient_id))         # existe ing
            if not filtro or filtro in ing.name.lower()             # pasa filtro
        ]

# ---------------------------------- evento -----------------------------------

    @rx.event
    async def load_stock(self):
        """Carga y filtra las filas de stock según la pestaña y la búsqueda."""
        filtro = self.search_text.lower()

        if self.selected_tab == "product":
            rows = self._product_rows(filtro)
            self.product_rows = rows
        else:
            rows = self._ingredient_rows(filtro)
            self.ingredient_rows = rows

        # paginación
        self.total_items = len(rows)
        self._page_data  = rows[self.offset : self.offset + self.limit]    

    # ═══════════════════════ MODAL ALTA ═══════════════════════════════
    @rx.event
    async def change_stock_type(self, value: str):
        """Al cambiar entre Producto / Ingrediente recarga las opciones."""
        self.stock_type = value
        self._reset_base_lists()

        if value == "Ingrediente":
            for ing in await select_all_ingredient_service():
                self.base_options.append(ing.name)
                self._base_map[ing.name] = str(ing.id)
        else:
            for p in await select_all_product_service():
                if p.product_type == ProductType.IN_STOCK:
                    self.base_options.append(p.name)
                    self._base_map[p.name] = str(p.id)
        self.set()

    # ---------- autocomplete ----------
    @rx.event
    def on_base_search(self, v:str):
        self.base_search = v or ""
        self.base_dropdown_open = True
        self.set()

    @rx.var
    def filtered_base_options(self) -> List[str]:
        if not self.base_search: return self.base_options
        t = self.base_search.lower()
        return [o for o in self.base_options if t in o.lower()]

    @rx.event
    def select_base(self, label:str):
        self.selected_base_label = label
        self.selected_base_id    = int(self._base_map[label])
        self.base_search         = label
        self.base_dropdown_open  = False
        self.set()

    # ---------- cantidades ----------
    @rx.event
    def change_quantity(self, v:str):     self.quantity     = float(v or 0)
    @rx.event
    def change_min_quantity(self, v:str): self.min_quantity = float(v or 0)

    @rx.event
    def reset_modal(self):
        self.stock_type = ""
        self.quantity   = 0
        self.min_quantity = 0
        self._reset_base_lists()
        self.set()

    def _reset_base_lists(self):
        self.base_search = ""
        self.selected_base_label = ""
        self.selected_base_id = None
        self.base_dropdown_open = False
        self.base_options = []
        self._base_map    = {}

    # ---------- submit alta ----------
    @rx.event
    async def submit_stock(self, form:dict):
        if self.selected_base_id is None:
            yield rx.toast("Debe seleccionar la base de stock", color_scheme="red"); return
        qty = float(form["quantity"]); mn = float(form["min_quantity"])
        try:
            if self.stock_type == "Ingrediente":
                await insert_ingredient_stock_service(self.selected_base_id, qty, mn)
            else:
                await insert_product_stock_service(self.selected_base_id, qty, mn)
            yield rx.toast("Stock guardado"); yield StockView.load_stock()
        except ValueError as e:
            yield rx.toast(str(e), color_scheme="red")

    # ═══════════════════════ MODAL EDICIÓN ═════════════════════════════
    @rx.event
    def open_edit_modal(self, stock_type:str, stock_id:int,
                        base_label:str, qty:float, mn:float):
        self.edit_stock_type   = stock_type
        self.edit_stock_id     = stock_id
        self.edit_base_label   = base_label
        self.edit_quantity     = qty
        self.edit_min_quantity = mn
        self.edit_modal_open   = True
        self.set()

    @rx.event
    async def set_edit_modal_open(self, is_open:bool):
        self.edit_modal_open = is_open
        self.set()

    @rx.event
    async def update_stock(self, form:dict):
        qty = float(form["quantity"]); mn = float(form["min_quantity"])
        try:
            if self.edit_stock_type == "Ingrediente":
                await update_ingredient_stock_service(self.edit_stock_id, qty, mn)
            else:
                await update_product_stock_service(self.edit_stock_id, qty, mn)
            yield rx.toast("Stock actualizado")
            self.edit_modal_open = False
            yield StockView.load_stock()
        except ValueError as e:
            yield rx.toast(str(e), color_scheme="red")

    # ════════════════════════ UI HELPERS ═══════════════════════════════
def get_title():
    return rx.text("Control de Stock", size="7", weight="bold",
                   color="#3E2723", fontFamily="DejaVu Sans Mono")

def stock_color(qty: float, min_qty: float) -> str:
    """Devuelve el color a usar en la celda según la cantidad."""
    if qty <= min_qty:          # rojo crítico
        return "#da1208"
    elif qty < min_qty + 3:     # naranja advertencia
        return "#e9910a"
    return "#3E2723"

# ─── pestañas ───────────────────────────────────────────────────────────
def tab_button(label: str, value: str):
    return rx.button(
        label,
        size="2",
        variant=rx.cond(StockView.selected_tab == value, "solid", "soft"),
        background_color=rx.cond(StockView.selected_tab == value, "#3E2723", "#A67B5B"),
        color="white",
        border_radius="0",
        padding_x="1.5em",
        on_click=lambda: StockView.set_tab(value),
    )

def tabs_bar():
    return rx.hstack(
        tab_button("Stock de Productos",   "product"),
        tab_button("Stock de Ingredientes","ingredient"),
        justify="center",
        gap="2",
        width="100%",
    )

def search_stock_component():
    return rx.input(
        placeholder="Buscar Stock",
        background_color="#3E2723",
        color="white",
        border_radius="8px",
        width="250px",
        on_change=StockView.on_search,
    )

# ─── modal alta ────────────────────────────────────────────────────────
def create_stock_form():
    return rx.form(
        rx.vstack(
            # Tipo
            rx.grid(
                rx.text("Tipo de Stock:", color="white"),
                rx.select(
                    StockView.type_options,
                    value=StockView.stock_type,
                    on_change=StockView.change_stock_type,
                    background_color="#3E2723",
                    color="white",
                ),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            # Base
            rx.grid(
                rx.text("Base de Stock:", color="white"),
                rx.vstack(
                    rx.box(
                        rx.input(
                            placeholder="Buscar…",
                            background_color="#5D4037",
                            color="white",
                            value=StockView.base_search,
                            on_change=StockView.on_base_search,
                        ),
                        rx.cond(
                            StockView.base_dropdown_open,
                            rx.vstack(
                                rx.foreach(
                                    StockView.filtered_base_options,
                                    lambda lbl: rx.box(
                                        rx.text(lbl, text_align="center", color="#3E2723"),
                                        on_click=lambda l=lbl: StockView.select_base(l),
                                        style={
                                            "padding": "0.5rem",
                                            "cursor": "pointer",
                                            "_hover": {"background_color": "#A67B5B",
                                                       "color": "white"},
                                        },
                                    ),
                                ),
                                background_color="#FFF8E1",
                                border="1px solid #A67B5B",
                                border_radius="0 0 8px 8px",
                                max_height="160px",
                                overflow_y="auto",
                                style={
                                    "position": "absolute", "top": "100%", "left": 0,
                                    "right": 0, "z_index": 1000},
                            ),
                        ),
                        style={"position": "relative", "width": "100%"},
                    ),
                    rx.input(name="stock_base", type="hidden",
                             value=StockView.selected_base_label),
                ),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            # Cantidades
            rx.grid(
                rx.text("Cantidad Actual:", color="white"),
                rx.input(type="number", name="quantity",
                         value=StockView.quantity,
                         on_change=StockView.change_quantity,
                         background_color="#3E2723", color="white"),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.grid(
                rx.text("Cantidad Mínima:", color="white"),
                rx.input(type="number",
                    name="min_quantity",
                    value=StockView.min_quantity,
                    on_change=StockView.change_min_quantity,
                    background_color="#3E2723",
                    color="white"
                ),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.divider(color="white"),
            rx.dialog.close(
                rx.button(rx.icon("save", size=22), "Guardar",
                          type="submit", background_color="#3E2723",
                          color="white", size="2", variant="solid"),
            ),
            spacing="3",
        ),
        on_submit=StockView.submit_stock,
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center", justify="center", debug=True,
    )

def create_stock_modal():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(rx.icon("plus", size=22),
                      background_color="#3E2723",
                      size="2", variant="solid",
                      on_click=StockView.reset_modal),
        ),
        rx.dialog.content(
            rx.flex(rx.dialog.title("Agregar Stock"),
                    create_stock_form(),
                    direction="column", align="center",
                    justify="center", gap="3"),
            background_color="#A67B5B",
            style={"max_width": "500px"}, padding="3",
        ),
    )

# ─── modal edición ─────────────────────────────────────────────────────
def edit_stock_form():
    return rx.form(
        rx.vstack(
            rx.grid(
                rx.text("Tipo de Stock:", color="white"),
                rx.input(read_only=True,
                         value=StockView.edit_stock_type,
                         background_color="#3E2723", color="white"),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.grid(
                rx.text("Base de Stock:", color="white"),
                rx.input(read_only=True,
                         value=StockView.edit_base_label,
                         background_color="#3E2723", color="white"),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.grid(
                rx.text("Cantidad Actual:", color="white"),
                rx.input(type="number", name="quantity",
                         value=StockView.edit_quantity,
                         on_change=StockView.change_edit_quantity,
                         background_color="#3E2723", color="white"),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.grid(
                rx.text("Cantidad Mínima:", color="white"),
                rx.cond(
                    AuthState.is_admin,
                    rx.input(
                        type="number",
                        name="min_quantity",
                        value=StockView.edit_min_quantity,
                        on_change=StockView.change_edit_min_quantity,
                        background_color="#3E2723",
                        color="white",
                        read_only=False,
                        is_disabled=False,
                    ),
                    rx.input(
                        type="number",
                        name="min_quantity",
                        value=StockView.edit_min_quantity,
                        on_change=StockView.change_edit_min_quantity,
                        background_color="#3E2723",
                        color="white",
                        read_only=True,
                        is_disabled=True,
                    ),
                ),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.divider(color="white"),
            rx.dialog.close(
                rx.button(rx.icon("save", size=22), "Actualizar",
                          type="submit", background_color="#3E2723",
                          color="white", size="2", variant="solid"),
            ),
            spacing="3",
        ),
        on_submit=StockView.update_stock,
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center", justify="center", debug=True,
    )

def edit_stock_modal():
    return rx.dialog.root(
        rx.dialog.content(
            rx.flex(rx.dialog.title("Editar Stock"),
                    edit_stock_form(),
                    direction="column", align="center",
                    justify="center", gap="3"),
            background_color="#A67B5B",
            style={"max_width": "500px"}, padding="3",
        ),
        open=StockView.edit_modal_open,
        on_open_change=StockView.set_edit_modal_open,
    )

# ─── acciones por fila ────────────────────────────────────────────────
def acciones_cell(row: dict, row_type: str):
    return rx.hstack(
        # ⬇️  antes:  rx.dialog.trigger( rx.button(...) )
        rx.button(
            rx.icon("square-pen", size=22),
            background_color="#3E2723",
            size="2",
            variant="solid",
            on_click=lambda _=None,
                     t=row_type,
                     sid=row["stock_id"],
                     lbl=row["name"],
                     q=row["qty"],
                     m=row["min"]: StockView.open_edit_modal(t, sid, lbl, q, m),
        ),
        spacing="2",
    )

def prod_row(r):
    col = r["color"]                            # ← ya viene precalculado
    return rx.table.row(
        rx.table.cell(r["name"], color=col),
        rx.table.cell(r["qty"],  color=col),
        rx.table.cell(r["min"],  color=col),
        rx.table.cell(acciones_cell(r, "Producto")),
        color="#3E2723",
    )

def ing_row(r):
    col = r["color"]
    return rx.table.row(
        rx.table.cell(r["name"],    color=col),
        rx.table.cell(r["qty"],     color=col),
        rx.table.cell(r["min"],     color=col),
        rx.table.cell(r["measure"], color=col),
        rx.table.cell(acciones_cell(r, "Ingrediente")),
        color="#3E2723",
    )

def get_table_header():
    return rx.table.row(
        rx.foreach(
            rx.cond(StockView.selected_tab == "product",
                    StockView.prod_columns, StockView.ing_columns),
            lambda c: rx.table.column_header_cell(c)),
        color="#3E2723", background_color="#A67B5B",
    )

def get_table_body(r): return rx.cond(
    StockView.selected_tab == "product", prod_row(r), ing_row(r),
)

# ─── paginación ─────────────────────────────────────────────────────────
def pagination_controls():
    return rx.hstack(
        rx.button(rx.icon("arrow-left", size=22),
                  on_click=StockView.prev_page,
                  is_disabled=StockView.offset <= 0,
                  background_color="#3E2723", size="2", variant="solid"),
        rx.text(StockView.current_page, " de ", StockView.num_total_pages),
        rx.button(rx.icon("arrow-right", size=22),
                  on_click=StockView.next_page,
                  is_disabled=StockView.offset + StockView.limit >= StockView.total_items,
                  background_color="#3E2723", size="2", variant="solid"),
        justify="center", color="#3E2723",
    )

# ─── main actions bar (incluye modal edición oculto) ───────────────────
def main_actions_bar():
    return rx.hstack(
        search_stock_component(),
        rx.cond(
            AuthState.is_admin,
            create_stock_modal(),
            None,
        ),
        edit_stock_modal(),
        justify="center", gap="3", width="80vw",
    )

# ─── página ─────────────────────────────────────────────────────────────
@rx.page(on_load=StockView.load_stock)
def stock():
    return rx.box(
        rx.vstack(
            get_title(), tabs_bar(), main_actions_bar(),
            rx.table.root(rx.table.header(get_table_header()),
                          rx.table.body(rx.foreach(StockView.page_rows, get_table_body)),
                          width="80vw", background_color="#FFF8E1",
                          border_radius="20px"),
            pagination_controls(),
            spacing="5", align="center", width="80vw",
        ),
        display="flex", justify_content="center", align_items="flex-start",
        text_align="center", background_color="#FDEFEA",
        width="92vw", height="80vh",
    )
