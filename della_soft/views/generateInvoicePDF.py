# della_soft/views/generateInvoicePDF.py

import os
from datetime import datetime
from fpdf import FPDF
from sqlmodel import Session, select
from num2words import num2words

from ..models import Invoice, Order, Customer, ProductOrder, Product
from ..repositories.ConnectDB import connect

def generate_invoice_pdf(order_id: int) -> str:
    engine = connect()
    with Session(engine) as session:
        # 1) Leemos la orden y el cliente
        order = session.get(Order, order_id)
        if not order:
            raise ValueError(f"No se encontró la orden con ID {order_id}")

        customer = session.get(Customer, order.id_customer)

        # 2) Buscamos detalles de productos
        detalles = session.exec(
            select(ProductOrder).where(ProductOrder.id_order == order_id)
        ).all()

        # 3) Calculamos subtotales de cada producto
        productos = []
        for det in detalles:
            producto = session.get(Product, det.id_product)
            productos.append({
                "nombre": producto.name,
                "cantidad": det.quantity,
                "precio_unitario": producto.price,
                "subtotal": det.quantity * producto.price
            })

        total = sum(p["subtotal"] for p in productos)
        iva = round(total / 11, 2)
        total_letras = num2words(total, lang='es').capitalize() + " guaranies"

        # 4) Verificamos si ya existe factura para esta orden
        existing = session.exec(
            select(Invoice).where(Invoice.id_order == order_id)
        ).one_or_none()

        if existing:
            nueva_factura = existing
        else:
            # 5) Si no existe, la creamos
            nueva_factura = Invoice(
                iva=iva,
                invoice_date=datetime.now(),
                id_order=order_id
            )
            session.add(nueva_factura)
            session.commit()
            session.refresh(nueva_factura)

        invoice_id = nueva_factura.id
        numero_factura = f"001-001-{invoice_id:06d}"

        # Extraemos variables antes de cerrar la sesión
        customer_first_name = customer.first_name
        customer_last_name  = customer.last_name
        customer_ci_div     = f"{customer.ci}-{customer.div}"
        fecha_emision       = datetime.today().strftime("%d/%m/%Y")

    # 6) Generamos el PDF con el mismo formato que ya tienes
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    pdf.cell(0, 10, "DELLA CAMPAGNA PASTELERIA", ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, "de Monique Augustini Lucienne Campagna Lalane", ln=True, align="C")
    pdf.cell(0, 5, "TORTAS FALSAS - FONDANT - MERENGUE - CHOCOLATE - FIGURAS DE AZUCAR - MESA DE DULCE", ln=True, align="C")
    pdf.cell(0, 5, "Sargento Ferreira N 195 c/ Tuyuti - Capiata, Paraguay", ln=True, align="C")
    pdf.cell(0, 5, "Tel: (0228) 631 209 / (0982) 493 185 / (0981) 446 692", ln=True, align="C")
    pdf.ln(3)

    pdf.cell(0, 6, "RUC: 1005125-2", ln=True)
    pdf.cell(0, 6, f"Factura N: {numero_factura}", ln=True)
    pdf.cell(0, 6, "Timbre N: 17376604", ln=True)
    pdf.cell(0, 6, "Autorizado por Resolucion General N 90/2024", ln=True)
    pdf.cell(0, 6, f"Fecha de Emision: {fecha_emision}", ln=True)
    pdf.cell(0, 6, "Condicion de Venta: CONTADO", ln=True)
    pdf.ln(5)

    pdf.cell(0, 8, f"Cliente: {customer_first_name} {customer_last_name}", ln=True)
    pdf.cell(0, 8, f"RUC: {customer_ci_div}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(20, 8, "CANT.", 1)
    pdf.cell(90, 8, "DESCRIPCION", 1)
    pdf.cell(40, 8, "PRECIO UNIT.", 1)
    pdf.cell(40, 8, "SUBTOTAL", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for p in productos:
        pdf.cell(20, 8, str(p["cantidad"]), 1)
        pdf.cell(90, 8, p["nombre"], 1)
        pdf.cell(40, 8, f"{p['precio_unitario']:,}", 1)
        pdf.cell(40, 8, f"{p['subtotal']:,}", 1)
        pdf.ln()

    pdf.ln(3)
    pdf.cell(0, 8, f"TOTAL IVA (10%): {iva:,.0f} Gs", ln=True)
    pdf.cell(0, 8, f"TOTAL A PAGAR: {total:,.0f} Gs", ln=True)
    pdf.multi_cell(0, 8, f"SON: {total_letras}", border="B")

    # 7) Guardamos en public/facturas y devolvemos la ruta absoluta
    base_dir   = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    public_dir = os.path.join(base_dir, "public", "facturas")
    os.makedirs(public_dir, exist_ok=True)
    filename   = os.path.join(public_dir, f"factura_{invoice_id}.pdf")
    pdf.output(filename)

    return filename
