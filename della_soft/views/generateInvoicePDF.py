# della_soft/views/GenerateInvoicePDF.py
import os
from hashlib import sha256
from datetime import datetime
from fpdf import FPDF
from sqlmodel import Session, select
from num2words import num2words

from ..models import (
    Invoice,
    Order,
    Customer,
    ProductOrder,
    Product,
    Stamped,
)
from ..repositories.ConnectDB import connect


def generate_invoice_pdf(order_id: int) -> str:
    """Genera (o recupera) la factura para un pedido y devuelve la ruta del PDF."""
    engine = connect()

    with Session(engine) as session:
        # ── 1. Datos básicos ──────────────────────────────────────────────────
        order: Order | None = session.get(Order, order_id)
        if not order:
            raise ValueError(f"No se encontró la orden con ID {order_id}")

        customer: Customer | None = session.get(Customer, order.id_customer)
        if not customer:
            raise ValueError(
                f"No se encontró el cliente con ID {order.id_customer}"
            )

        detalles = session.exec(
            select(ProductOrder).where(ProductOrder.id_order == order_id)
        ).all()

        productos = []
        for det in detalles:
            producto = session.get(Product, det.id_product)
            productos.append(
                {
                    "nombre": producto.name,
                    "cantidad": det.quantity,
                    "precio_unitario": producto.price,
                    "subtotal": det.quantity * producto.price,
                }
            )

        total = sum(p["subtotal"] for p in productos)
        iva = round(total / 11, 2)  # 10 % IVA incluido → 1/11 del total
        total_letras = (
            num2words(total, lang="es").capitalize() + " guaranies"
        )

        # ── 2. Timbrado activo y secuencia ───────────────────────────────────
        stamped: Stamped | None = session.exec(
            select(Stamped).where(Stamped.active.is_(True))
        ).first()
        if stamped is None:
            raise RuntimeError("No hay timbrado activo en la base")

        # Reservamos la secuencia
        stamped.current_sequence += 1
        if stamped.current_sequence > stamped.max_sequence:
            raise RuntimeError("El timbrado activo agotó su numeración")

        sec = stamped.current_sequence
        numero_factura = f"{stamped.establishment}-{stamped.expedition_point}-{sec:06d}"

        # ── 3. Crear / obtener Invoice ───────────────────────────────────────
        invoice = session.exec(
            select(Invoice).where(Invoice.id_order == order_id)
        ).one_or_none()

        if invoice is None:
            invoice = Invoice(
                iva=iva,
                invoice_date=datetime.now(),
                id_order=order_id,
                id_stamped=stamped.id,
                nro_factura=numero_factura,
            )
            session.add(invoice)
        else:
            # Si existe, actualizamos por si se llamó nuevamente
            invoice.iva = iva
            invoice.invoice_date = invoice.invoice_date or datetime.now()
            invoice.id_stamped = invoice.id_stamped or stamped.id
            invoice.nro_factura = invoice.nro_factura or numero_factura

        session.commit()        # guarda Invoice y actualización de Stamped
        session.refresh(invoice)

        # ── 4. Variables simples necesarias fuera del contexto ──────────────
        invoice_id = invoice.id
        cliente_full = f"{customer.first_name} {customer.last_name}"
        cliente_ruc = (
            f"{customer.ci}"
            if customer.div is None
            else f"{customer.ci}-{customer.div}"
        )
        fecha_emision = invoice.invoice_date.strftime("%d/%m/%Y")
        timbrado_num    = stamped.stamped_number

    # ── 5. Render del PDF (fuera de la sesión) ───────────────────────────────
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    # Encabezado del negocio
    pdf.cell(0, 10, "DELLA CAMPAGNA PASTELERIA", ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(
        0,
        5,
        "de Monique Augustini Lucienne Campagna Lalane",
        ln=True,
        align="C",
    )
    pdf.cell(
        0,
        5,
        "TORTAS FALSAS - FONDANT - MERENGUE - CHOCOLATE - FIGURAS DE AZUCAR - MESA DE DULCE",
        ln=True,
        align="C",
    )
    pdf.cell(
        0,
        5,
        "Sargento Ferreira N 195 c/ Tuyuti - Capiata, Paraguay",
        ln=True,
        align="C",
    )
    pdf.cell(
        0,
        5,
        "Tel: (0228) 631 209 / (0982) 493 185 / (0981) 446 692",
        ln=True,
        align="C",
    )
    pdf.ln(3)

    # Datos de la factura
    pdf.cell(0, 6, "RUC: 1005125-2", ln=True)
    pdf.cell(0, 6, f"Factura N: {invoice.nro_factura}", ln=True)
    pdf.cell(0, 6, f"Timbrado N: {timbrado_num}", ln=True)
    pdf.cell(0, 6, "Autorizado por Resolucion General N 90/2024", ln=True)
    pdf.cell(0, 6, f"Fecha de Emision: {fecha_emision}", ln=True)
    pdf.cell(0, 6, "Condicion de Venta: CONTADO", ln=True)
    pdf.ln(5)

    # Datos del cliente
    pdf.cell(0, 8, f"Cliente: {cliente_full}", ln=True)
    pdf.cell(0, 8, f"RUC: {cliente_ruc}", ln=True)
    pdf.ln(4)

    # Detalle de productos
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

    # ── 6. Guardado del archivo ─────────────────────────────────────────────
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    public_dir = os.path.join(base_dir, "public", "facturas")
    os.makedirs(public_dir, exist_ok=True)
    filename = os.path.join(public_dir, f"factura_{invoice_id}.pdf")
    pdf.output(filename)

    # ── 7. Guardamos hash del PDF (opcional, pero útil para auditoría) ─────
    with open(filename, "rb") as fh:
        file_hash = sha256(fh.read()).hexdigest()

    with Session(engine) as session:
        inv: Invoice | None = session.get(Invoice, invoice_id)
        if inv:
            inv.pdf_hash = inv.pdf_hash or file_hash
            session.add(inv)
            session.commit()

    return filename
