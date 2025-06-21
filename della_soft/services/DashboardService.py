from ..repositories.ProductRepository import select_all as select_all_products
from ..repositories.ProductStockRepository import select_all as select_all_product_stocks
from ..repositories.ProductOrderRepository import select_all as select_all_product_orders
from ..repositories.OrderRepository import select_all as select_all_orders
from datetime import date, timedelta

async def get_stock_rotation_data_month():
    productos = select_all_products()
    product_stocks = select_all_product_stocks()  # Trae TODAS las filas ProductStock
    product_orders = select_all_product_orders()
    orders = select_all_orders()

    mes_actual = date.today().month
    anho_actual = date.today().year

    data = []
    for producto in productos:
        # Buscar el stock actual directo (NO sumar, solo el valor actual cargado para ese producto)
        fila_stock = next((ps for ps in product_stocks if ps.product_id == producto.id), None)
        stock_disponible = fila_stock.quantity if fila_stock else 0

        cantidad_vendida_mes = sum(
            po.quantity for po in product_orders
            if po.id_product == producto.id and
                any(
                    o.id == po.id_order and
                    o.order_date and
                    o.order_date.month == mes_actual and
                    o.order_date.year == anho_actual
                    for o in orders
                )
        )

        data.append({
            "Producto": producto.name,
            "Stock Disponible": stock_disponible,
            "Cantidad Vendida (Rotación)": cantidad_vendida_mes
        })
    return data


async def get_top_products_month():
    productos = select_all_products()
    product_orders = select_all_product_orders()
    orders = select_all_orders()

    mes_actual = date.today().month
    anho_actual = date.today().year

    ventas = []
    for producto in productos:
        cantidad_vendida = sum([
            po.quantity for po in product_orders
            if po.id_product == producto.id and
                any(
                    o.id == po.id_order and
                    o.order_date.month == mes_actual and
                    o.order_date.year == anho_actual
                    for o in orders
                )
        ])
        ventas.append({
            "Producto": producto.name,
            "Cantidad Vendida": cantidad_vendida
        })
    ventas.sort(key=lambda x: x["Cantidad Vendida"], reverse=True)
    return ventas[:5]

async def get_orders_per_day_month():
    orders = select_all_orders()
    mes_actual = date.today().month
    anho_actual = date.today().year

    today = date.today()
    primer_dia = today.replace(day=1)
    if mes_actual == 12:
        primer_dia_siguiente_mes = primer_dia.replace(year=anho_actual+1, month=1)
    else:
        primer_dia_siguiente_mes = primer_dia.replace(month=mes_actual+1)
    dias = (primer_dia_siguiente_mes - primer_dia).days

    conteo = { (primer_dia + timedelta(days=i)).strftime("%d/%m") : 0 for i in range(dias) }

    for order in orders:
        if order.order_date.month == mes_actual and order.order_date.year == anho_actual:
            clave = order.order_date.strftime("%d/%m")
            if clave in conteo:
                conteo[clave] += 1

    return [{"Fecha": k, "Pedidos": v} for k, v in sorted(conteo.items())]
