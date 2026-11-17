"""Genera un reporte paginado del cálculo y sus tablas."""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from matplotlib import get_data_path
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, LongTable, Paragraph, SimpleDocTemplate, Spacer

from utilidades.comparaciones import Calculo
from utilidades.exportacion import columnas
from utilidades.formato import mostrar


def guardar_pdf(ruta: str | Path, calculo: Calculo, campos: dict, datos: list,
                fecha: datetime, figura: Figure | None, decimales: int) -> None:
    """Escribe el informe con la gráfica y los datos del cálculo registrado."""
    documento = SimpleDocTemplate(str(ruta), title=f"NumLab - {calculo.modulo}",
                                  leftMargin=38, rightMargin=38,
                                  topMargin=46, bottomMargin=50)
    estilos = getSampleStyleSheet()
    fuentes = Path(get_data_path()) / "fonts" / "ttf"
    if "NumLabSans" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("NumLabSans", str(fuentes / "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("NumLabSansBold", str(fuentes / "DejaVuSans-Bold.ttf")))
    for estilo in ("Normal", "BodyText"):
        estilos[estilo].fontName = "NumLabSans"
    for estilo in ("Title", "Heading2", "Heading3"):
        estilos[estilo].fontName = "NumLabSansBold"
    estilos["Title"].textColor = colors.HexColor("#102d4b")
    estilos["BodyText"].splitLongWords = True
    estilos["Normal"].leading = 13
    celda = estilos["Normal"].clone("Celda", fontSize=7, leading=9, alignment=TA_CENTER)

    def parrafo(texto: object, estilo: str = "BodyText") -> Paragraph:
        return Paragraph(escape(str(texto)).replace("\n", "<br/>"), estilos[estilo])

    elementos = [parrafo("NumLab", "Title"),
                 parrafo(f"{calculo.modulo} · {fecha:%d/%m/%Y %H:%M:%S}", "Heading2"),
                 parrafo("Datos y parámetros", "Heading2"),
                 parrafo("\n".join(f"{k} = {v}" for k, v in campos.items() if v))]
    if datos:
        elementos.append(parrafo("Datos tabulados", "Heading3"))

    def tabla(filas: list[dict]) -> None:
        claves = columnas(filas)
        # Las tablas anchas se dividen por columnas y conservan el identificador.
        paso = 6
        for inicio in range(1, max(2, len(claves)), paso):
            grupo = claves[:1] + claves[inicio:inicio + paso]
            matriz = [[Paragraph(escape(k), celda) for k in grupo]]
            matriz.extend([Paragraph(escape(mostrar(f[k], decimales)) if k in f else "", celda)
                           for k in grupo] for f in filas)
            cuadricula = LongTable(matriz, colWidths=[documento.width / len(grupo)] * len(grupo),
                                  repeatRows=1)
            cuadricula.setStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#bedbe6")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef4f8")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, 0), .6, colors.HexColor("#46798c")),
            ])
            elementos.extend([cuadricula, Spacer(1, 8)])

    if datos:
        tabla([{"Fila": i, "x": x, "y": y} for i, (x, y) in enumerate(datos, 1)])
    elementos.append(parrafo("Resultados y errores", "Heading2"))
    tabla(calculo.resumen)
    if calculo.detalles:
        elementos.append(parrafo(calculo.detalles))
    if figura is not None:
        buffer = BytesIO()
        tamano = figura.get_size_inches().copy()
        try:
            figura.set_size_inches(7, 3.25, forward=False)
            figura.savefig(buffer, format="png", dpi=120)
        finally:
            figura.set_size_inches(tamano, forward=False)
        buffer.seek(0)
        ancho, alto = 7, 3.25
        ancho_reporte = min(documento.width, 270 * ancho / alto)
        elementos.extend([parrafo("Gráfica seleccionada", "Heading2"),
                          Image(buffer, width=ancho_reporte, height=ancho_reporte * alto / ancho)])
    for nombre, r in calculo.resultados.items():
        elementos.extend([parrafo(nombre, "Heading2"), parrafo(r.mensaje)])
        if r.tabla:
            tabla(r.tabla)

    def pie(canvas, doc) -> None:
        canvas.setFillColor(colors.HexColor("#465f78"))
        canvas.setFont("NumLabSans", 8)
        canvas.drawString(38, 30, "NumLab · Laboratorio Interactivo de Métodos Numéricos")
        canvas.drawRightString(doc.pagesize[0] - 38, 30, str(doc.page))

    documento.build(elementos, onFirstPage=pie, onLaterPages=pie)
