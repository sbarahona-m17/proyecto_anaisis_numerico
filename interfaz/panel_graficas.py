"""Pestañas con figuras Matplotlib integradas a Tkinter."""
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from graficas.vistas import dibujar, vistas
from utilidades.comparaciones import Calculo


class LienzoGrafica(FigureCanvasTkAgg):
    """Espera a que Tk asigne espacio al panel antes de dibujarlo."""

    def draw(self) -> None:
        ancho, alto = self.get_width_height()
        if ancho >= 160 and alto >= 150:
            super().draw()


class BarraGrafica(NavigationToolbar2Tk):
    """Localiza las acciones de navegación de Matplotlib."""
    toolitems = (
        ("Inicio", "Restaurar vista", "home", "home"),
        ("Atrás", "Vista anterior", "back", "back"),
        ("Adelante", "Vista siguiente", "forward", "forward"),
        (None, None, None, None),
        ("Mover", "Arrastrar para desplazar", "move", "pan"),
        ("Zoom", "Seleccionar un rectángulo", "zoom_to_rect", "zoom"),
        ("Guardar", "Exportar gráfica", "filesave", "save_figure"),
    )

    def __init__(self, canvas, master, guardar):
        self.guardar = guardar
        super().__init__(canvas, master, pack_toolbar=False)

    def save_figure(self, *args) -> None:
        """Abre el diálogo de exportación a PNG de NumLab."""
        self.guardar()


class Graficas(ttk.Frame):
    """Crea las figuras al seleccionar su pestaña."""

    def __init__(self, master: tk.Misc, guardar):
        super().__init__(master)
        self.guardar = guardar
        self.libro = ttk.Notebook(self)
        self.libro.pack(fill="both", expand=True)
        self.libro.bind("<<NotebookTabChanged>>", self.actualizar)
        self.figuras: dict[str, tuple] = {}
        self.calculo: Calculo | None = None
        self.oscuro = False
        self.paso = None
        self.limpiar()

    def _retirar(self) -> None:
        for id_pestana in self.libro.tabs():
            self.libro.nametowidget(id_pestana).destroy()
        self.figuras.clear()

    def limpiar(self) -> None:
        """Presenta un estado vacío dentro del panel."""
        self._retirar()
        self.calculo = None
        self.paso = None
        marco = ttk.Frame(self.libro)
        ttk.Label(marco, text="Calcula un problema para ver su gráfica.",
                  style="Nota.TLabel").place(relx=.5, rely=.5, anchor="center")
        self.libro.add(marco, text="Gráficas")

    def cargar(self, calculo: Calculo, oscuro: bool) -> None:
        """Instala las vistas disponibles para el nuevo cálculo."""
        self._retirar()
        self.calculo, self.oscuro, self.paso = calculo, oscuro, None
        for nombre in vistas(calculo):
            self.libro.add(ttk.Frame(self.libro), text=nombre)
        if not self.libro.tabs():
            self.limpiar()
        else:
            self.actualizar()

    def actualizar(self, evento: tk.Event | None = None, forzar: bool = False) -> None:
        """Dibuja la pestaña seleccionada si todavía no está actualizada."""
        actual = self.libro.select()
        if not actual or self.calculo is None:
            return
        if actual not in self.figuras:
            marco = self.libro.nametowidget(actual)
            figura = Figure(figsize=(6, 3), dpi=100, layout="constrained")
            canvas = LienzoGrafica(figura, master=marco)
            toolbar = BarraGrafica(canvas, marco, self.guardar)
            toolbar.pack(side="bottom", fill="x")
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.figuras[actual] = (figura, canvas, toolbar, object())
        figura, canvas, toolbar, anterior = self.figuras[actual]
        estado = (self.paso, self.oscuro)
        if anterior != estado or forzar:
            dibujo = vistas(self.calculo, self.paso)[self.libro.tab(actual, "text")]
            dibujar(figura, dibujo, self.oscuro)
            toolbar.update()
            canvas.draw_idle()
            self.figuras[actual] = (figura, canvas, toolbar, estado)

    def figura(self) -> Figure | None:
        """Devuelve la figura visible para exportarla."""
        self.actualizar()
        conjunto = self.figuras.get(self.libro.select())
        return conjunto[0] if conjunto else None
