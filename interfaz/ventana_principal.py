"""Pantalla inicial, navegación y sesión de NumLab."""
from dataclasses import dataclass
from datetime import datetime
from queue import Empty, SimpleQueue
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from interfaz import (estilos, panel_ayuda, panel_derivacion, panel_edo,
                      panel_integracion, panel_interpolacion, panel_raices)
from interfaz.panel_comparacion import encabezado
from interfaz.panel_graficas import Graficas
from interfaz.portada import Trazo
from interfaz.tabla_resultados import Tabla, TablaEditable
from utilidades.comparaciones import METODOS, Calculo, calcular
from utilidades.ejemplos import D2, EJEMPLOS, I1, N3
from utilidades.exportacion import guardar_csv, leer_csv
from utilidades.formato import mostrar
from utilidades.reporte import guardar_pdf
from utilidades.validaciones import entero

PANELES = dict(zip(METODOS, (panel_raices, panel_derivacion, panel_interpolacion,
                            panel_integracion, panel_edo)))
TITULOS = {"Raíces": "Cálculo de raíces", "Diferenciación": "Diferenciación numérica",
           "Interpolación": "Interpolación polinomial", "Integración": "Integración numérica",
           "EDO": "Ecuaciones diferenciales"}
DESCRIPCIONES = ("Busca ceros y analiza convergencia.",
                 "Estima derivadas con cinco nodos.",
                 "Construye polinomios desde datos.",
                 "Calcula áreas con reglas de cuadratura.",
                 "Compara soluciones de valor inicial.")
ICONOS = ("f(x)", "d/dx", "P(x)", "∫", "y′")
DATOS = {"Diferenciación": D2, "Interpolación": I1, "Integración": N3}
FILAS_FORMULARIO = {
    "Raíces": ((("f",), ("a", "b"), ("x0",), ("s0", "s1")),
               (("criterio",), ("tol", "max_iter")), (("referencia",),)),
    "Diferenciación": ((("modo",), ("f",), ("x0", "h")), (), ()),
    "Interpolación": ((("consultas",),), (), ()),
    "Integración": ((("modo",), ("f",), ("a", "b")), (("n",), ("unidad",)), ()),
    "EDO": ((("f",), ("t0", "tf"), ("y0",)),
            (("paso",), ("h", "n")), (("exacta",),)),
}
EJEMPLO_VACIO = "Elegir un caso…"
ETIQUETAS_FORMULARIO = {
    "a": "Límite a", "b": "Límite b", "s0": "Semilla secante x₀", "s1": "Semilla secante x₁",
    "tol": "Tolerancia", "max_iter": "Máx. iteraciones", "h": "Paso h",
}


@dataclass
class Registro:
    """Conserva entradas y resultados de una ejecución de la sesión."""
    calculo: Calculo
    metodo: str
    campos: dict[str, str]
    datos: list
    fecha: datetime
    decimales: int
    ejemplo: str


class Aplicacion(tk.Tk):
    """Coordina la interfaz y mantiene el cálculo fuera del hilo de eventos."""

    def __init__(self):
        super().__init__()
        self.title("NumLab · Laboratorio Interactivo de Métodos Numéricos")
        ancho = min(1390, self.winfo_screenwidth() - 60)
        alto = min(890, self.winfo_screenheight() - 105)
        self.geometry(f"{ancho}x{alto}")
        self.minsize(990, 580)
        self.estilo = ttk.Style(self)
        self.oscuro = False
        self.colores = estilos.aplicar(self.estilo, self.oscuro)
        self.configure(background=self.colores["fondo"])
        self.historial: list[Registro] = []
        self.registro: Registro | None = None
        self.modulo: str | None = None
        self.trabajo = 0
        self.reloj = None
        self.indice = None
        self._barra_lateral()
        espacio = ttk.Frame(self)
        espacio.pack(side="left", fill="both", expand=True)
        self.estado = tk.StringVar()
        ttk.Label(espacio, textvariable=self.estado, style="Estado.TLabel",
                  padding=(20, 7)).pack(side="bottom", fill="x")
        self.cuerpo = ttk.Frame(espacio)
        self.cuerpo.pack(fill="both", expand=True)
        self.inicio()

    def _barra_lateral(self) -> None:
        """Mantiene los módulos y las acciones generales accesibles."""
        barra = ttk.Frame(self, style="Hero.TFrame", width=172, padding=(10, 15, 10, 10))
        barra.pack(side="left", fill="y")
        barra.pack_propagate(False)
        ttk.Label(barra, text="NumLab", style="Marca.TLabel").pack(anchor="w", padx=9, pady=(5, 16))
        ttk.Separator(barra).pack(fill="x", padx=9, pady=(0, 12))
        self.navegacion = {}
        nombre_inicio = ttk.Button(barra, text="Inicio", style="Barra.TButton", command=self.inicio)
        nombre_inicio.pack(fill="x", pady=(0, 4))
        self.navegacion[None] = nombre_inicio
        for modulo in METODOS:
            nombre = "Ecuaciones (EDO)" if modulo == "EDO" else modulo
            boton = ttk.Button(barra, text=nombre, style="Barra.TButton",
                               command=lambda m=modulo: self.abrir_modulo(m))
            boton.pack(fill="x", pady=1)
            self.navegacion[modulo] = boton
        utilidades = ttk.Frame(barra, style="Hero.TFrame")
        utilidades.pack(side="bottom", fill="x")
        ttk.Separator(utilidades).pack(fill="x", padx=9, pady=(0, 8))
        ttk.Button(utilidades, text="Historial", style="Barra.TButton",
                   command=self.abrir_historial).pack(fill="x")
        ttk.Button(utilidades, text="Ayuda", style="Barra.TButton", command=lambda: panel_ayuda.abrir(
            self, self.colores)).pack(fill="x")
        self.tema = ttk.Button(utilidades, text="Tema oscuro", style="Barra.TButton",
                               command=self.alternar_tema)
        self.tema.pack(fill="x")

    def _marcar_modulo(self) -> None:
        self.colores = estilos.aplicar(self.estilo, self.oscuro, self.modulo)
        for modulo, boton in self.navegacion.items():
            boton.state(["selected" if modulo == self.modulo else "!selected"])

    def report_callback_exception(self, tipo, valor, traceback) -> None:
        """Conserva la sesión si un evento de la interfaz falla."""
        messagebox.showerror("NumLab", str(valor) or "Ocurrió un error en esta operación.",
                             parent=self)

    def _renovar(self) -> None:
        self.pausar()
        self.trabajo += 1
        self.registro = None
        for hijo in self.cuerpo.winfo_children():
            hijo.destroy()

    def inicio(self) -> None:
        """Muestra el menú de módulos."""
        self._renovar()
        self.modulo = None
        self._marcar_modulo()
        hero = ttk.Frame(self.cuerpo, style="Hero.TFrame", padding=(25, 16))
        hero.pack(fill="x", padx=23, pady=(22, 18))
        portada = ttk.Frame(hero, style="Hero.TFrame")
        portada.pack(side="left", fill="y", pady=(12, 0))
        ttk.Label(portada, text="Laboratorio de\nmétodos numéricos",
                  style="Hero.TLabel").pack(anchor="w")
        ttk.Label(portada, text="Compara métodos, visualiza sus pasos y exporta tus resultados.",
                  style="DescripcionHero.TLabel", wraplength=290, justify="left").pack(
                      anchor="w", pady=(9, 0))
        Trazo(hero).pack(side="right", fill="both", expand=True, padx=(22, 0))
        ttk.Label(self.cuerpo, text="Módulos de cálculo", style="Seccion.TLabel").pack(
            anchor="w", padx=23, pady=(0, 8))
        tarjetas = ttk.Frame(self.cuerpo)
        tarjetas.pack(fill="x", padx=17)
        for i, (modulo, descripcion) in enumerate(zip(METODOS, DESCRIPCIONES)):
            tarjeta = ttk.Frame(tarjetas, style="Tarjeta.TFrame", padding=(11, 7))
            tarjeta.grid(row=i // 2, column=i % 2, sticky="ew", padx=6, pady=(0, 10))
            accion = lambda m=modulo: self.abrir_modulo(m)
            fondo_icono, tinta_icono = estilos.acento_modulo(modulo, self.oscuro)
            icono = tk.Label(tarjeta, text=ICONOS[i], width=4, background=fondo_icono,
                             foreground=tinta_icono, font=("Cambria Math", 15),
                             cursor="hand2", borderwidth=0)
            icono.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 11), pady=3)
            ttk.Button(tarjeta, text=TITULOS[modulo], style="Tarjeta.TButton",
                       command=accion, cursor="hand2").grid(row=0, column=1, sticky="ew")
            nota = ttk.Label(tarjeta, text=descripcion, style="PanelNota.TLabel", cursor="hand2")
            nota.grid(row=1, column=1, sticky="w", padx=4, pady=(0, 4))
            flecha = ttk.Button(tarjeta, text="→", width=2, style="Tarjeta.TButton",
                                command=accion, takefocus=False)
            flecha.grid(row=0, column=2, rowspan=2, padx=(5, 1))
            tarjeta.columnconfigure(1, weight=1)
            nota.bind("<Button-1>", lambda _, abrir=accion: abrir())
            icono.bind("<Button-1>", lambda _, abrir=accion: abrir())
        for columna in range(2):
            tarjetas.columnconfigure(columna, weight=1, uniform="tarjetas")
        self.estado.set("Elige un módulo para iniciar un cálculo.")

    def abrir_modulo(self, modulo: str) -> None:
        """Construye el espacio de trabajo del módulo solicitado."""
        self._renovar()
        self.modulo = modulo
        self._marcar_modulo()
        top = ttk.Frame(self.cuerpo, padding=(19, 14, 19, 8))
        top.pack(fill="x")
        ttk.Label(top, text=TITULOS[modulo], style="Titulo.TLabel").pack(side="left")
        ttk.Button(top, text="Volver", command=self.volver).pack(side="right")
        ttk.Button(top, text="Teoría", command=lambda: panel_ayuda.abrir(
            self, self.colores, self.metodo.get())).pack(side="right", padx=(0, 6))
        metodos = ttk.Frame(self.cuerpo, padding=(19, 0, 19, 10))
        metodos.pack(fill="x")
        self.metodo = tk.StringVar(value=METODOS[modulo][0])
        self.comparar = tk.BooleanVar()
        self.seleccion_metodo = (self.metodo.get(), self.comparar.get())
        ttk.Checkbutton(metodos, text="Comparación", variable=self.comparar,
                        command=self._actualizar_campos).pack(side="right", padx=(10, 0))
        for nombre in METODOS[modulo]:
            ttk.Radiobutton(metodos, text=nombre, value=nombre, variable=self.metodo,
                            style="Metodo.TRadiobutton",
                            command=self._actualizar_campos).pack(side="left", padx=(0, 5))
        partes = ttk.Panedwindow(self.cuerpo, orient="horizontal")
        partes.pack(fill="both", expand=True, padx=19, pady=(0, 11))
        controles = ttk.Frame(partes, width=269, style="Tarjeta.TFrame", padding=(12, 10))
        partes.add(controles, weight=0)
        salida = ttk.Frame(partes, style="Tarjeta.TFrame")
        partes.add(salida, weight=1)
        self._formulario(controles)
        self._salida(salida)
        self._actualizar_campos()
        self.estado.set("Selecciona un método, ingresa los datos y pulsa Calcular.")

    def _formulario(self, master: ttk.Frame) -> None:
        ttk.Label(master, text="Datos y parámetros", style="FormularioTitulo.TLabel",
                  padding=(10, 8)).pack(fill="x", pady=(0, 10))
        cabecera = ttk.Frame(master, style="Tarjeta.TFrame", padding=(8, 6))
        cabecera.pack(fill="x", pady=(0, 9))
        ttk.Label(cabecera, text="Ejemplos oficiales", style="Campo.TLabel").pack(anchor="w")
        self.ejemplo = tk.StringVar(value=EJEMPLO_VACIO)
        opciones = ttk.Combobox(cabecera, textvariable=self.ejemplo,
                               values=list(EJEMPLOS[self.modulo]), width=18, state="readonly")
        opciones.pack(fill="x", pady=(3, 0))
        opciones.bind("<<ComboboxSelected>>", self.cargar_ejemplo)
        botones = ttk.Frame(master, style="Panel.TFrame")
        botones.pack(side="bottom", fill="x", pady=(10, 0))
        ttk.Separator(botones).pack(fill="x", pady=(0, 8))
        self.boton_calcular = ttk.Button(botones, text="Calcular", style="Accion.TButton",
                                         command=self.ejecutar)
        self.boton_calcular.pack(side="left", padx=(0, 7), fill="x", expand=True)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")
        self.lienzo = tk.Canvas(master, width=225, highlightthickness=0,
                                background=self.colores["papel"])
        scroll = ttk.Scrollbar(master, command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.formulario = ttk.Frame(self.lienzo, padding=(0, 0, 8, 0), style="Panel.TFrame")
        interior = self.lienzo.create_window((0, 0), window=self.formulario, anchor="nw")
        self.formulario.bind("<Configure>", lambda _: self.lienzo.configure(
            scrollregion=self.lienzo.bbox("all")))
        self.lienzo.bind("<Configure>", lambda e: self.lienzo.itemconfigure(interior, width=e.width))
        def desplazar(evento: tk.Event) -> None:
            self.lienzo.yview_scroll(-int(evento.delta / 120), "units")

        self.lienzo.bind("<MouseWheel>", desplazar)
        self.formulario.bind("<MouseWheel>", desplazar)
        self.variables: dict[str, tk.StringVar] = {}
        self.cajas: dict[str, ttk.Frame] = {}
        self.predeterminados = {}
        self.primer_campo = None
        entradas, ajustes, opcionales = FILAS_FORMULARIO[self.modulo]
        self.grupos_formulario = []
        for titulo, filas in (("Entradas", entradas),
                              ("Cálculo", ajustes), (None, (*opcionales, ("decimales",)))):
            grupo = ttk.Frame(self.formulario, style="Panel.TFrame")
            if titulo:
                ttk.Label(grupo, text=titulo, style="Grupo.TLabel").grid(row=0, column=0, sticky="w")
                ttk.Separator(grupo).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 7))
            self.grupos_formulario.append((grupo, filas))
            for columna in range(2):
                grupo.columnconfigure(columna, weight=1, uniform="campo")
        self.grupo_opciones = self.grupos_formulario[-1][0]
        self.opciones_abiertas = False
        self.boton_opciones = ttk.Button(self.formulario, text="▸  Opciones adicionales",
                                        command=self._alternar_opciones, style="Tarjeta.TButton")
        padres = {clave: grupo for grupo, filas in self.grupos_formulario
                  for fila in filas for clave in fila}
        for clave, etiqueta, defecto in (*PANELES[self.modulo].CAMPOS,
                                         ("decimales", "Decimales (0 a 15)", "8")):
            inicial = defecto[0] if isinstance(defecto, tuple) else defecto
            self.predeterminados[clave] = inicial
            variable = tk.StringVar(value=inicial)
            self.variables[clave] = variable
            marco = ttk.Frame(padres[clave], style="Panel.TFrame")
            self.cajas[clave] = marco
            etiqueta_campo = ttk.Label(marco, text=ETIQUETAS_FORMULARIO.get(clave, etiqueta),
                                       style="Campo.TLabel")
            etiqueta_campo.pack(anchor="w")
            etiqueta_campo.bind("<MouseWheel>", desplazar)
            if isinstance(defecto, tuple):
                campo = ttk.Combobox(marco, textvariable=variable, values=defecto,
                                      width=10, state="readonly")
                campo.bind("<<ComboboxSelected>>", self._actualizar_campos)
            else:
                estilo = "Expresion.TEntry" if clave == "f" else "TEntry"
                campo = ttk.Entry(marco, textvariable=variable, width=10, style=estilo)
                campo.bind("<Return>", lambda _: self.ejecutar())
                if self.primer_campo is None:
                    self.primer_campo = campo
            campo.pack(fill="x", pady=(2, 2))
            if not isinstance(campo, ttk.Combobox):
                campo.bind("<MouseWheel>", desplazar)
            marco.bind("<MouseWheel>", desplazar)
        self.tabla_entrada = None
        if self.modulo in DATOS:
            self.datos_marco = ttk.Frame(self.formulario, style="Panel.TFrame")
            ttk.Label(self.datos_marco, text="Nodos", style="Grupo.TLabel").pack(anchor="w")
            ttk.Label(self.datos_marco, text="Doble clic para editar una celda.",
                      style="Campo.TLabel").pack(anchor="w")
            self.tabla_entrada = TablaEditable(self.datos_marco)
            self.tabla_entrada.oscuro = self.oscuro
            self.tabla_entrada.pack(fill="x", pady=(3, 4))
            self.tabla_entrada.puntos(DATOS[self.modulo])
            acciones = ttk.Frame(self.datos_marco, style="Panel.TFrame")
            acciones.pack(fill="x")
            for texto, accion in (("Añadir", self.tabla_entrada.agregar),
                                  ("Eliminar", self.tabla_entrada.eliminar),
                                  ("Importar CSV", self.importar)):
                ttk.Button(acciones, text=texto, command=accion,
                           style="Compacto.TButton").pack(side="left", padx=(0, 3))

    def _salida(self, master: ttk.Frame) -> None:
        self.titulo_resultado = tk.StringVar(value="Resultados")
        self.mensaje = tk.StringVar(value="Los resultados aparecen aquí después del cálculo.")
        cabecera = ttk.Frame(master, style="Acento.TFrame", padding=(14, 10, 14, 9))
        cabecera.pack(fill="x")
        ttk.Label(cabecera, textvariable=self.titulo_resultado, style="Resultado.TLabel").pack(
            anchor="w")
        mensaje = ttk.Label(cabecera, textvariable=self.mensaje, style="ResultadoNota.TLabel")
        mensaje.pack(anchor="w", pady=(1, 0))
        cabecera.bind("<Configure>", lambda e: mensaje.configure(wraplength=max(200, e.width - 28)))
        ttk.Separator(master).pack(fill="x")
        fila = ttk.Frame(master, style="Panel.TFrame", padding=(8, 5))
        fila.pack(side="bottom", fill="x")
        self.exportadores = []
        for nombre, accion in (("CSV", self.exportar_csv), ("PNG", self.exportar_png),
                               ("PDF", self.exportar_pdf)):
            boton = ttk.Button(fila, text=nombre, command=accion, state="disabled", width=4,
                               style="Compacto.TButton")
            boton.pack(side="left", padx=(0, 3))
            self.exportadores.append(boton)
        ttk.Separator(fila, orient="vertical").pack(side="left", fill="y", padx=(6, 8))
        self.animadores = []
        for nombre, accion in (("Anterior", lambda: self.avanzar(-1)),
                               ("Siguiente", lambda: self.avanzar(1)),
                               ("Reproducir", self.reproducir), ("Pausar", self.pausar)):
            boton = ttk.Button(fila, text=nombre, command=accion, state="disabled",
                               style="Compacto.TButton")
            boton.pack(side="left", padx=(0, 2))
            self.animadores.append(boton)
        self.velocidad = tk.DoubleVar(value=3)
        ttk.Label(fila, text="Velocidad", style="Campo.TLabel").pack(side="left", padx=(7, 2))
        ttk.Scale(fila, from_=1, to=8, variable=self.velocidad, length=63).pack(side="left")
        self.vistas_trabajo = ttk.Notebook(master, style="Espacio.TNotebook")
        self.vistas_trabajo.pack(fill="both", expand=True, padx=7, pady=(5, 0))
        self.vistas_trabajo.enable_traversal()
        self.graficas = Graficas(self.vistas_trabajo, self.exportar_png)
        self.resultados = ttk.Notebook(self.vistas_trabajo)
        self.vistas_trabajo.add(self.graficas, text="Gráficas")
        self.vistas_trabajo.add(self.resultados, text="Tablas y detalles")
        self.tablas: dict[str, Tabla] = {}
        self._tabla("Resumen", [])

    def _tabla(self, titulo: str, filas: list[dict]) -> None:
        tabla = Tabla(self.resultados)
        etiqueta = titulo.replace("Trapecio ", "T. ").replace("Simpson 1/3 ", "S. ")
        self.resultados.add(tabla, text=etiqueta)
        tabla.cargar(filas, self.registro.decimales if self.registro else 8, oscuro=self.oscuro)
        self.tablas[titulo] = tabla

    def _actualizar_campos(self, evento: tk.Event | None = None) -> None:
        seleccion = (self.metodo.get(), self.comparar.get())
        if seleccion != self.seleccion_metodo:
            self.seleccion_metodo = seleccion
            if self.registro is not None or self.boton_calcular.instate(["disabled"]):
                self._vaciar_salida()
            self.estado.set("Ingresa los datos y pulsa Calcular.")
        if evento is not None or self.registro is not None:
            self.pausar()
        campos = {k: v.get() for k, v in self.variables.items()}
        claves = PANELES[self.modulo].visibles(self.metodo.get(), campos, self.comparar.get())
        claves.add("decimales")
        for clave, marco in self.cajas.items():
            marco.grid_forget()
        for grupo, _ in self.grupos_formulario:
            grupo.pack_forget()
        self.boton_opciones.pack_forget()
        if self.tabla_entrada is not None:
            self.datos_marco.pack_forget()
        for indice, (grupo, filas) in enumerate(self.grupos_formulario):
            if grupo is self.grupo_opciones:
                self.boton_opciones.pack(fill="x", pady=(0, 4))
                if self.opciones_abiertas:
                    grupo.pack(fill="x")
            elif any(clave in claves for fila in filas for clave in fila):
                grupo.pack(fill="x", pady=(0, 9))
            for fila, campos_fila in enumerate(filas, start=2):
                visibles = [clave for clave in campos_fila if clave in claves]
                for columna, clave in enumerate(visibles):
                    self.cajas[clave].grid(row=fila, column=columna, sticky="ew",
                                          columnspan=3 - len(visibles),
                                          padx=(0, 4) if len(visibles) == 2 and columna == 0 else 0,
                                          pady=(0, 5))
            if indice == 0 and self.tabla_entrada is not None and (
                    self.modulo == "Interpolación" or campos.get("modo") == "Tabla"):
                self.datos_marco.pack(fill="x", pady=(0, 11))
        self.lienzo.yview_moveto(0)

    def _alternar_opciones(self) -> None:
        self.opciones_abiertas = not self.opciones_abiertas
        if self.opciones_abiertas:
            self.boton_opciones.configure(text="▾  Opciones adicionales")
            self.grupo_opciones.pack(fill="x")
            self.lienzo.update_idletasks()
            self.lienzo.yview_moveto(1)
        else:
            self.boton_opciones.configure(text="▸  Opciones adicionales")
            self.grupo_opciones.pack_forget()

    def cargar_ejemplo(self, evento: tk.Event | None = None) -> None:
        """Restaura parámetros y carga todas las entradas del ejemplo."""
        datos = EJEMPLOS[self.modulo][self.ejemplo.get()]
        for k, variable in self.variables.items():
            variable.set(str(datos.get(k, self.predeterminados[k])))
        self.metodo.set(datos.get("metodo", METODOS[self.modulo][0]))
        if self.tabla_entrada is not None:
            self.tabla_entrada.puntos(datos.get("datos", DATOS[self.modulo]))
        self._actualizar_campos()

    def importar(self) -> None:
        """Solicita y carga un CSV de dos columnas."""
        ruta = filedialog.askopenfilename(parent=self, title="Importar nodos",
                                           filetypes=[("Tabla CSV", "*.csv")])
        if ruta:
            try:
                datos = leer_csv(ruta)
                self.tabla_entrada.puntos(datos)
                self.estado.set(f"Se importaron {len(datos)} filas.")
            except (ValueError, OSError) as error:
                messagebox.showerror("Importar CSV", str(error), parent=self)

    def volver(self) -> None:
        """Regresa a los datos desde resultados o al inicio desde el formulario."""
        if self.registro is None:
            self.inicio()
        else:
            self._vaciar_salida()
            if (self.primer_campo is not None
                    and self.primer_campo.winfo_ismapped()):
                self.primer_campo.focus_set()
            self.estado.set("Datos listos para editar y calcular de nuevo.")

    def _vaciar_salida(self) -> None:
        self.pausar()
        self.trabajo += 1
        self.registro = None
        self.indice = None
        self.boton_calcular.configure(state="normal")
        self.graficas.limpiar()
        for tabla in self.tablas.values():
            tabla.destroy()
        self.tablas.clear()
        self._tabla("Resumen", [])
        self.titulo_resultado.set("Resultados")
        self.mensaje.set("Los resultados aparecen aquí después del cálculo.")
        for boton in self.exportadores + self.animadores:
            boton.configure(state="disabled")

    def limpiar(self) -> None:
        """Borra datos editables y restablece las opciones de presentación."""
        self._vaciar_salida()
        for clave, variable in self.variables.items():
            campo = next(c for c in self.cajas[clave].winfo_children() if isinstance(c, ttk.Entry))
            if not isinstance(campo, ttk.Combobox) and clave != "decimales":
                variable.set("")
            else:
                variable.set(self.predeterminados[clave])
        if self.tabla_entrada is not None:
            self.tabla_entrada.puntos([])
        self.ejemplo.set(EJEMPLO_VACIO)
        self._actualizar_campos()
        self.estado.set("Entradas y resultados limpiados.")

    def ejecutar(self) -> None:
        """Captura las entradas y ejecuta los métodos en un hilo de trabajo."""
        if self.boton_calcular.instate(["disabled"]):
            return
        campos = {k: v.get() for k, v in self.variables.items()}
        try:
            decimales = entero(campos["decimales"], "Decimales", 0, 15)
        except ValueError as error:
            messagebox.showerror("Entrada inválida", str(error), parent=self)
            return
        datos = (self.tabla_entrada.datos() if self.tabla_entrada is not None and
                 (self.modulo == "Interpolación" or campos.get("modo") == "Tabla") else [])
        self._vaciar_salida()
        self.boton_calcular.configure(state="disabled")
        self.estado.set("Calculando…")
        id_trabajo, modulo, metodo = self.trabajo, self.modulo, self.metodo.get()
        comparar, ejemplo = self.comparar.get(), self.ejemplo.get()
        fecha = datetime.now()
        cola = SimpleQueue()

        def resolver() -> None:
            try:
                resultado = calcular(modulo, metodo, campos, datos, comparar)
                cola.put(Registro(resultado, metodo, campos, datos, fecha, decimales, ejemplo))
            except Exception as error:
                cola.put(error)

        def consultar() -> None:
            if self.trabajo != id_trabajo:
                return
            try:
                elemento = cola.get_nowait()
            except Empty:
                self.after(35, consultar)
                return
            self.boton_calcular.configure(state="normal")
            if isinstance(elemento, Exception):
                self.estado.set("Revisa los datos y vuelve a calcular.")
                messagebox.showerror("No se pudo calcular", str(elemento), parent=self)
            else:
                self.historial.append(elemento)
                self.mostrar_resultado(elemento)

        Thread(target=resolver, daemon=True).start()
        self.after(35, consultar)

    def mostrar_resultado(self, registro: Registro) -> None:
        """Presenta un cálculo nuevo o recuperado del historial."""
        self._vaciar_salida()
        self.registro = registro
        calculo, d = registro.calculo, registro.decimales
        self.titulo_resultado.set(encabezado(calculo, d))
        self.tablas["Resumen"].cargar(calculo.resumen, d, oscuro=self.oscuro)
        detalles = []
        campos_internos = {"función", "puntos", "componentes", "curva", "expandido",
                           "iniciales", "método", "exacta", "resumen"}
        for nombre, r in calculo.resultados.items():
            if r.tabla:
                self._tabla(nombre, r.tabla)
            detalles.append({"Método": nombre, "Dato": "Mensaje", "Valor": r.mensaje})
            detalles.extend({"Método": nombre, "Dato": k, "Valor": mostrar(v, d)}
                            for k, v in r.extra.items() if k not in campos_internos)
        if calculo.detalles:
            detalles.append({"Dato": "Interpretación", "Valor": calculo.detalles})
        self._tabla("Detalles", detalles)
        self.tablas["Detalles"].arbol.column("2", width=620, anchor="w")
        self.graficas.cargar(calculo, self.oscuro)
        if self.graficas.calculo is None:
            self.vistas_trabajo.select(self.resultados)
        primero = next(iter(calculo.resultados.values()))
        self.mensaje.set(calculo.detalles if calculo.comparacion and calculo.detalles
                         else primero.mensaje if not calculo.comparacion
                         else "Consulta el resumen para ver el estado de cada método.")
        if calculo.comparacion:
            self.estado.set(encabezado(calculo, d))
        else:
            cantidad = primero.extra.get("Iteraciones", primero.extra.get("Pasos", len(primero.tabla)))
            self.estado.set(f"{primero.mensaje} · Registros de cálculo: {cantidad}")
        for boton in self.exportadores:
            boton.configure(state="normal")
        if self.longitud_animacion() > 1:
            for boton in self.animadores:
                boton.configure(state="normal")

    def _guardar(self, extension: str, formato: str, accion) -> None:
        if self.registro is None:
            return
        ruta = filedialog.asksaveasfilename(parent=self, title=f"Exportar {formato}",
                                             defaultextension=extension,
                                             filetypes=[(formato, f"*{extension}")])
        if ruta:
            try:
                accion(ruta)
                self.estado.set(f"Guardado: {ruta}")
            except (ValueError, OSError) as error:
                messagebox.showerror(f"Exportar {formato}", str(error), parent=self)

    def exportar_csv(self) -> None:
        """Exporta la tabla seleccionada."""
        tabla = self.resultados.nametowidget(self.resultados.select())
        self._guardar(".csv", "Tabla CSV", lambda ruta: guardar_csv(ruta, tabla.filas))

    def exportar_png(self) -> None:
        """Exporta la gráfica visible."""
        figura = self.graficas.figura()
        if figura is not None:
            self._guardar(".png", "Gráfica PNG", lambda ruta: figura.savefig(ruta, dpi=160))
        elif self.registro is not None:
            self.estado.set("El cálculo seleccionado no tiene una gráfica disponible.")

    def exportar_pdf(self) -> None:
        """Exporta un reporte del cálculo registrado."""
        r = self.registro
        if r is not None:
            nombres = {k: nombre for k, nombre, _ in PANELES[r.calculo.modulo].CAMPOS}
            autorizados = PANELES[r.calculo.modulo].visibles(
                r.metodo, r.campos, r.calculo.comparacion)
            campos = {nombres[k]: v for k, v in r.campos.items() if k in autorizados}
            campos["Método"] = "Comparación" if r.calculo.comparacion else r.metodo
            campos["Decimales"] = r.campos["decimales"]
            self._guardar(".pdf", "Reporte PDF", lambda ruta: guardar_pdf(
                ruta, r.calculo, campos, r.datos, r.fecha, self.graficas.figura(), r.decimales))

    def longitud_animacion(self) -> int:
        """Cuenta las filas reales disponibles para reproducir."""
        if self.registro is None:
            return 0
        return max((len(r.tabla) for r in self.registro.calculo.resultados.values()), default=0)

    def avanzar(self, salto: int) -> None:
        """Resalta la fila y dibuja el prefijo de iteraciones correspondiente."""
        limite = self.longitud_animacion() - 1
        if limite < 0:
            return
        if self.indice is None:
            self.indice = 0 if salto > 0 else max(0, limite - 1)
            modulo = self.registro.calculo.modulo
            preferida = {"Raíces": "Geometría", "Diferenciación": "Nodos y tangente",
                         "Interpolación": ("Bases de Lagrange" if self.registro.metodo == "Lagrange"
                                           else "Parciales de Newton"),
                         "EDO": "Soluciones"}.get(modulo)
            for pestana in self.graficas.libro.tabs():
                if self.graficas.libro.tab(pestana, "text") == preferida:
                    self.graficas.libro.select(pestana)
                    break
            if self.registro.metodo in self.tablas:
                self.resultados.select(self.tablas[self.registro.metodo])
        else:
            self.indice = max(0, min(limite, self.indice + salto))
        for tabla in self.tablas.values():
            tabla.enfocar_fila(self.indice)
        self.graficas.paso = self.indice
        self.graficas.actualizar()
        self.estado.set(f"Animación · registro {self.indice + 1} de {limite + 1}")

    def reproducir(self) -> None:
        """Inicia la reproducción mediante eventos programados."""
        if self.reloj is not None or self.longitud_animacion() < 2:
            return
        if self.indice == self.longitud_animacion() - 1:
            self.indice = None

        def siguiente() -> None:
            self.reloj = None
            self.avanzar(1)
            if self.indice is not None and self.indice < self.longitud_animacion() - 1:
                self.reloj = self.after(int(1000 / self.velocidad.get()), siguiente)
        siguiente()

    def pausar(self) -> None:
        """Detiene el temporizador de reproducción."""
        if self.reloj is not None:
            self.after_cancel(self.reloj)
            self.reloj = None

    def alternar_tema(self) -> None:
        """Cambia la paleta sin perder el cálculo ni el formulario."""
        self.oscuro = not self.oscuro
        self.colores = estilos.aplicar(self.estilo, self.oscuro, self.modulo)
        self.configure(background=self.colores["fondo"])
        self.tema.configure(text="Tema claro" if self.oscuro else "Tema oscuro")
        if self.modulo is None:
            self.inicio()
            return
        self.lienzo.configure(background=self.colores["papel"])
        if self.tabla_entrada is not None:
            datos = self.tabla_entrada.datos()
            self.tabla_entrada.oscuro = self.oscuro
            self.tabla_entrada.puntos(datos)
        for tabla in self.tablas.values():
            tabla.arbol.tag_configure("alterna", background=self.colores["alterna"])
        self.graficas.oscuro = self.oscuro
        self.graficas.actualizar()

    def abrir_historial(self) -> None:
        """Muestra cálculos de la sesión y permite recuperar uno."""
        ventana = tk.Toplevel(self)
        ventana.title("NumLab · Historial de la sesión")
        ventana.geometry("670x330")
        ventana.transient(self)
        tabla = Tabla(ventana)
        tabla.pack(fill="both", expand=True, padx=10, pady=10)
        tabla.cargar([{"Hora": r.fecha.strftime("%H:%M:%S"),
                      "Módulo": r.calculo.modulo, "Método": r.metodo,
                      "Vista": "Comparación" if r.calculo.comparacion else "Individual",
                      "Ejemplo": r.ejemplo if "·" in r.ejemplo else "Datos propios"}
                     for r in self.historial], oscuro=self.oscuro)

        def recuperar(evento: tk.Event | None = None) -> None:
            ids = tabla.arbol.selection()
            if not ids:
                return
            r = self.historial[int(ids[0])]
            ventana.destroy()
            self.abrir_modulo(r.calculo.modulo)
            for clave, valor in r.campos.items():
                self.variables[clave].set(valor)
            self.metodo.set(r.metodo)
            self.comparar.set(r.calculo.comparacion)
            self.ejemplo.set(r.ejemplo)
            if self.tabla_entrada is not None and r.datos:
                self.tabla_entrada.puntos(r.datos)
            self._actualizar_campos()
            self.mostrar_resultado(r)

        tabla.arbol.bind("<Double-1>", recuperar)
        ttk.Button(ventana, text="Recuperar cálculo", command=recuperar).pack(pady=(0, 10))
