"""Tablas desplazables con edición para los datos de entrada."""
import tkinter as tk
from tkinter import font, ttk

from interfaz.estilos import PALETAS
from utilidades.exportacion import columnas
from utilidades.formato import mostrar


class Tabla(ttk.Frame):
    """Envuelve un Treeview con desplazamiento en ambos ejes."""

    def __init__(self, master: tk.Misc, altura: int = 6):
        super().__init__(master)
        self.arbol = ttk.Treeview(self, show="headings", height=altura)
        self.fuente = font.Font(root=self, font=ttk.Style(self).lookup("Treeview", "font"))
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.arbol.yview)
        horizontal = ttk.Scrollbar(self, orient="horizontal", command=self.arbol.xview)
        self.arbol.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.arbol.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.filas: list[dict] = []

    def cargar(self, filas: list[dict], decimales: int = 8,
               claves: list[str] | None = None, oscuro: bool = False) -> None:
        """Carga el esquema y los valores, identificando ausencias."""
        self.filas = filas
        claves = claves or columnas(filas)
        self.arbol.delete(*self.arbol.get_children())
        self.arbol.configure(columns=[str(i) for i in range(len(claves))])
        textos = [[mostrar(fila[c], decimales) if c in fila else "" for c in claves] for fila in filas]
        for i, clave in enumerate(claves):
            valores = [fila[clave] for fila in filas[:100] if fila.get(clave) is not None]
            numerica = bool(valores) and all(isinstance(v, (int, float)) for v in valores)
            alineacion = "e" if numerica else "w"
            self.arbol.heading(str(i), text=clave, anchor=alineacion)
            muestra = [clave, *(fila[i] for fila in textos[:100])]
            ancho = max(47, min(270, max(self.fuente.measure(t) for t in muestra) + 22))
            self.arbol.column(str(i), anchor=alineacion, minwidth=42, width=ancho)
        self.arbol.tag_configure("alterna", background=PALETAS[oscuro]["alterna"])
        for i, valores in enumerate(textos):
            self.arbol.insert("", "end", iid=str(i), values=valores,
                              tags=("alterna",) if i % 2 else ())

    def enfocar_fila(self, i: int) -> None:
        """Resalta la fila correspondiente a una iteración visible."""
        if self.arbol.exists(str(i)):
            self.arbol.selection_set(str(i))
            self.arbol.see(str(i))


class TablaEditable(Tabla):
    """Permite editar cada celda con doble clic y confirmar con Intro."""

    def __init__(self, master: tk.Misc):
        super().__init__(master, altura=5)
        self.oscuro = False
        self.editor: ttk.Entry | None = None
        self.arbol.bind("<Double-1>", self.editar)
        self.arbol.bind("<F2>", self.editar_seleccion)

    def datos(self) -> list[tuple[str, str]]:
        """Devuelve todas las filas, incluidas las que requieren completar datos."""
        self.confirmar()
        return [tuple(self.arbol.item(i, "values")) for i in self.arbol.get_children()]

    def puntos(self, puntos: list) -> None:
        """Reemplaza los datos de la tabla."""
        self.cancelar()
        self.cargar([{"x": str(x), "y": str(y)} for x, y in puntos],
                    claves=["x", "y"], oscuro=self.oscuro)
        for columna in ("0", "1"):
            self.arbol.column(columna, width=94)

    def agregar(self) -> None:
        """Añade una fila editable y abre su primera celda."""
        puntos = self.datos() + [("", "")]
        self.puntos(puntos)
        fila = str(len(puntos)-1)
        self.arbol.see(fila)
        self.after_idle(lambda: self._abrir(fila, "#1"))

    def eliminar(self) -> None:
        """Elimina las filas seleccionadas."""
        seleccionadas = set(self.arbol.selection())
        self.puntos([p for i, p in enumerate(self.datos()) if str(i) not in seleccionadas])

    def cancelar(self) -> None:
        """Cierra el editor activo."""
        if self.editor is not None:
            editor, self.editor = self.editor, None
            editor.destroy()

    def confirmar(self) -> None:
        """Persiste el texto del editor antes de leer la tabla."""
        if self.editor is not None:
            fila, columna = self.celda
            self.arbol.set(fila, columna, self.editor.get())
            self.cancelar()

    def editar(self, evento: tk.Event) -> None:
        """Abre la celda apuntada."""
        self._abrir(self.arbol.identify_row(evento.y), self.arbol.identify_column(evento.x))

    def editar_seleccion(self, evento: tk.Event) -> None:
        """Abre la primera celda de la fila activa con F2."""
        self._abrir(self.arbol.focus(), "#1")

    def _abrir(self, fila: str, columna: str) -> None:
        self.confirmar()
        if not fila or columna not in ("#1", "#2"):
            return
        caja = self.arbol.bbox(fila, columna)
        if not caja:
            return
        x, y, w, h = caja
        self.celda = fila, columna
        self.editor = ttk.Entry(self.arbol)
        self.editor.insert(0, self.arbol.set(fila, columna))
        self.editor.select_range(0, "end")
        self.editor.place(x=x, y=y, width=w, height=h)
        self.editor.focus_set()
        self.editor.bind("<Return>", lambda _: self.confirmar())
        self.editor.bind("<FocusOut>", lambda _: self.confirmar())
        self.editor.bind("<Escape>", lambda _: self.cancelar())
