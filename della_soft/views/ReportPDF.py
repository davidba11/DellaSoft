from fpdf import FPDF
import os
from datetime import datetime

EMPRESA = "Della Campagna Pastelería"
MES_ACTUAL = datetime.now().strftime('%m/%Y')
LOGO_PATH = os.path.join("assets", "logo.png")  # El logo debe estar aquí

class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=80, y=8, w=50)
            self.set_y(65)  # 8 + 50 (altura logo) + 7
        else:
            self.set_y(20)

    def tabla_centrada(self, encabezados, datos, ancho_col):
        total_ancho = sum(ancho_col)
        x_inicio = (210 - total_ancho) / 2  # A4 = 210mm
        self.set_x(x_inicio)
        self.set_font("Arial", "B", 12)
        for i, h in enumerate(encabezados):
            self.cell(ancho_col[i], 8, h, 1, 0, "C")
        self.ln()
        self.set_font("Arial", "", 12)
        for fila in datos:
            self.set_x(x_inicio)
            for i, valor in enumerate(fila):
                self.cell(ancho_col[i], 8, str(valor), 1, 0, "C")
            self.ln()

def generate_stock_rotation_pdf(data):
    pdf = PDF()
    pdf.add_page()
    # --- Contenido debajo del logo ---
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, EMPRESA, 0, 1, "C")
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Reporte de Stock Disponible vs Rotación ({MES_ACTUAL})", 0, 1, "C")
    pdf.ln(6)
    encabezados = ["Producto", "Stock", "Rotación (Vendido)"]
    ancho_col = [60, 40, 60]
    filas = [[item["Producto"], item["Stock Disponible"], item["Cantidad Vendida (Rotación)"]] for item in data]
    pdf.tabla_centrada(encabezados, filas, ancho_col)
    if not os.path.exists("assets"):
        os.makedirs("assets")
    output_path = "stock_rotation_report.pdf"
    pdf.output(os.path.join("assets", output_path))
    return f"/{output_path}"

def generate_top_products_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, EMPRESA, 0, 1, "C")
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Top 5 Productos Más Vendidos ({MES_ACTUAL})", 0, 1, "C")
    pdf.ln(6)
    encabezados = ["Producto", "Cantidad Vendida"]
    ancho_col = [80, 40]
    filas = [[item["Producto"], item["Cantidad Vendida"]] for item in data]
    pdf.tabla_centrada(encabezados, filas, ancho_col)
    if not os.path.exists("assets"):
        os.makedirs("assets")
    output_path = "top_products_report.pdf"
    pdf.output(os.path.join("assets", output_path))
    return f"/{output_path}"

def generate_orders_per_day_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, EMPRESA, 0, 1, "C")
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Cantidad de Pedidos por Día ({MES_ACTUAL})", 0, 1, "C")
    pdf.ln(6)
    encabezados = ["Fecha", "Pedidos"]
    ancho_col = [40, 40]
    filas = [[item["Fecha"], item["Pedidos"]] for item in data]
    pdf.tabla_centrada(encabezados, filas, ancho_col)
    if not os.path.exists("assets"):
        os.makedirs("assets")
    output_path = "orders_per_day_report.pdf"
    pdf.output(os.path.join("assets", output_path))
    return f"/{output_path}"
