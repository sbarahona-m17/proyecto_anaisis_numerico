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
ACENTOS = ("#51ceb1", "#7fa9f0", "#a69aeb", "#f1b773", "#eb91a3")
DATOS = {"Diferenciación": D2, "Interpolación": I1, "Integración": N3}


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
        ancho = min(1240, self.winfo_screenwidth() - 45)
        alto = min(850, self.winfo_screenheight() - 105)
        self.geometry(f"{ancho}x{alto}")
        self.minsize(920, 580)
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
        self.barra = ttk.Frame(self, style="Hero.TFrame", padding=(22, 9))
        self.barra.pack(fill="x")
        ttk.Label(self.barra, text="NumLab", style="Marca.TLabel").pack(side="left")
        ttk.Button(self.barra, text="Inicio", style="Barra.TButton", command=self.inicio).pack(side="left", padx=(18, 4))
        ttk.Button(self.barra, text="Ayuda", style="Barra.TButton", command=lambda: panel_ayuda.abrir(
            self, self.colores)).pack(side="right", padx=3)
        self.tema = ttk.Button(self.barra, text="Tema oscuro", style="Barra.TButton", command=self.alternar_tema)
        self.tema.pack(side="right", padx=3)
        ttk.Button(self.barra, text="Historial", style="Barra.TButton", command=self.abrir_historial).pack(
            side="right", padx=3)
        self.estado = tk.StringVar()
        ttk.Label(self, textvariable=self.estado, style="Estado.TLabel",
                  padding=(14, 6)).pack(side="bottom", fill="x")
        self.cuerpo = ttk.Frame(self)
        self.cuerpo.pack(fill="both", expand=True)
        self.inicio()

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
        hero = ttk.Frame(self.cuerpo, style="Hero.TFrame", padding=(25, 10))
        hero.pack(fill="x", padx=22, pady=(17, 14))
        portada = ttk.Frame(hero, style="Hero.TFrame")
        portada.pack(side="left", fill="y")
        ttk.Label(portada, text="NumLab", style="Hero.TLabel").pack(anchor="w")
        ttk.Label(portada, text="Laboratorio Interactivo de Métodos Numéricos",
                  style="Subhero.TLabel", wraplength=460).pack(anchor="w")
        ttk.Label(portada, text="Explora aproximaciones y compara cómo cambia el error.",
                  style="DescripcionHero.TLabel", wraplength=430).pack(anchor="w", pady=(5, 9))
        ttk.Button(portada, text="Comenzar con raíces  →", style="Accion.TButton",
                   command=lambda: self.abrir_modulo("Raíces")).pack(anchor="w", pady=(0, 4))
        Trazo(hero).pack(side="right", fill="both", expand=True, padx=(26, 0))
        ttk.Label(self.cuerpo, text="Elige un módulo", style="Seccion.TLabel").pack(
            anchor="w", padx=24, pady=(0, 3))
        tarjetas = ttk.Frame(self.cuerpo, padding=(16, 0))
        tarjetas.pack(fill="x")
        for i, (modulo, descripcion) in enumerate(zip(METODOS, DESCRIPCIONES)):
            tarjeta = ttk.Frame(tarjetas, style="Panel.TFrame", padding=(9, 5))
            tarjeta.grid(row=i//2, column=i%2, sticky="ew", padx=6, pady=4)
            accion = lambda m=modulo: self.abrir_modulo(m)
            icono = tk.Label(tarjeta, text=ICONOS[i], width=4, background=ACENTOS[i],
                             foreground="#172640", font=("Segoe UI Semibold", 12),
                             cursor="hand2", borderwidth=0)
            icono.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=3)
            ttk.Button(tarjeta, text=f"{TITULOS[modulo]}  →", style="Tarjeta.TButton",
                       command=accion, cursor="hand2").grid(row=0, column=1, sticky="ew")
            nota = ttk.Label(tarjeta, text=descripcion, background=self.colores["papel"],
                             foreground=self.colores["secundario"], cursor="hand2")
            nota.grid(row=1, column=1, sticky="ew", padx=13, pady=(0, 4))
            tarjeta.columnconfigure(1, weight=1)
            nota.bind("<Button-1>", lambda _, abrir=accion: abrir())
            icono.bind("<Button-1>", lambda _, abrir=accion: abrir())
        for columna in range(2):
            tarjetas.columnconfigure(columna, weight=1, uniform="tarjetas")
        self.estado.set("Ingeniería de Software  ·  Métodos Numéricos  ·  2026-2")

    def abrir_modulo(self, modulo: str) -> None:
        """Construye el espacio de trabajo del módulo solicitado."""
        self._renovar()
        self.modulo = modulo
        top = ttk.Frame(self.cuerpo, padding=(12, 5))
        top.pack(fill="x")
        ttk.Button(top, text="Volver", command=self.volver).grid(row=0, column=0, padx=(0, 8))
        ttk.Label(top, text=TITULOS[modulo], style="Titulo.TLabel").grid(row=0, column=1, sticky="w")
        top.columnconfigure(1, weight=1)
        self.metodo = tk.StringVar(value=METODOS[modulo][0])
        lista = ttk.Combobox(top, textvariable=self.metodo, values=METODOS[modulo],
                             width=23, state="readonly")
        lista.grid(row=0, column=2, padx=4)
        lista.bind("<<ComboboxSelected>>", self._actualizar_campos)
        ttk.Button(top, text="Teoría", command=lambda: panel_ayuda.abrir(
            self, self.colores, self.metodo.get())).grid(row=0, column=3, padx=4)
        self.comparar = tk.BooleanVar()
        ttk.Checkbutton(top, text="Comparación", variable=self.comparar,
                        command=self._actualizar_campos).grid(row=0, column=4, padx=4)
        partes = ttk.Panedwindow(self.cuerpo, orient="horizontal")
        partes.pack(fill="both", expand=True, padx=12, pady=(0, 4))
        controles = ttk.Frame(partes, width=300, padding=(4, 2, 4, 4))
        partes.add(controles, weight=0)
        vertical = ttk.Panedwindow(partes, orient="vertical")
        partes.add(vertical, weight=1)
        self.graficas = Graficas(vertical, self.exportar_png)
        vertical.add(self.graficas, weight=3)
        salida = ttk.Frame(vertical, height=230)
        vertical.add(salida, weight=2)
        self._formulario(controles)
        self._salida(salida)
        vertical.bind("<Map>", lambda _: vertical.after_idle(
            lambda: self._ajustar_sash(vertical)), add="+")
        self._actualizar_campos()
        self.estado.set("Selecciona un método, ingresa los datos y pulsa Calcular.")

    @staticmethod
    def _ajustar_sash(vertical: ttk.Panedwindow) -> None:
        if vertical.winfo_exists():
            vertical.sashpos(0, int(vertical.winfo_height() * .61))

    def _formulario(self, master: ttk.Frame) -> None:
        cabecera = ttk.Frame(master)
        cabecera.pack(fill="x", pady=(0, 6))
        ttk.Label(cabecera, text="Datos y parámetros", style="Seccion.TLabel").pack(anchor="w")
        self.ejemplo = tk.StringVar(value="Seleccionar ejemplo oficial")
        opciones = ttk.Combobox(cabecera, textvariable=self.ejemplo,
                               values=list(EJEMPLOS[self.modulo]), width=31, state="readonly")
        opciones.pack(fill="x", pady=(4, 0))
        opciones.bind("<<ComboboxSelected>>", self.cargar_ejemplo)
        botones = ttk.Frame(master)
        botones.pack(side="bottom", fill="x", pady=(5, 0))
        self.boton_calcular = ttk.Button(botones, text="Calcular", style="Accion.TButton",
                                         command=self.ejecutar)
        self.boton_calcular.pack(side="left", padx=(0, 4))
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")
        self.lienzo = tk.Canvas(master, width=265, highlightthickness=0,
                                background=self.colores["fondo"])
        scroll = ttk.Scrollbar(master, command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.formulario = ttk.Frame(self.lienzo, padding=(0, 0, 6, 0))
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
        for clave, etiqueta, defecto in (*PANELES[self.modulo].CAMPOS,
                                         ("decimales", "Decimales (0 a 15)", "8")):
            inicial = defecto[0] if isinstance(defecto, tuple) else defecto
            self.predeterminados[clave] = inicial
            variable = tk.StringVar(value=inicial)
            self.variables[clave] = variable
            marco = ttk.Frame(self.formulario)
            self.cajas[clave] = marco
            ttk.Label(marco, text=etiqueta).pack(anchor="w")
            if isinstance(defecto, tuple):
                campo = ttk.Combobox(marco, textvariable=variable, values=defecto,
                                      width=20, state="readonly")
                campo.bind("<<ComboboxSelected>>", self._actualizar_campos)
            else:
                campo = ttk.Entry(marco, textvariable=variable, width=20)
                campo.bind("<Return>", lambda _: self.ejecutar())
                if self.primer_campo is None:
                    self.primer_campo = campo
            campo.pack(fill="x", pady=(2, 2))
            if not isinstance(campo, ttk.Combobox):
                campo.bind("<MouseWheel>", desplazar)
            marco.bind("<MouseWheel>", desplazar)
        self.tabla_entrada = None
        if self.modulo in DATOS:
            self.datos_marco = ttk.Frame(self.formulario)
            ttk.Label(self.datos_marco, text="Nodos (doble clic para editar)").pack(anchor="w")
            self.tabla_entrada = TablaEditable(self.datos_marco)
            self.tabla_entrada.oscuro = self.oscuro
            self.tabla_entrada.pack(fill="x", pady=(3, 4))
            self.tabla_entrada.puntos(DATOS[self.modulo])
            acciones = ttk.Frame(self.datos_marco)
            acciones.pack(fill="x")
            for texto, accion in (("Añadir", self.tabla_entrada.agregar),
                                  ("Eliminar", self.tabla_entrada.eliminar),
                                  ("Importar CSV", self.importar)):
                ttk.Button(acciones, text=texto, command=accion).pack(side="left")

    def _salida(self, master: ttk.Frame) -> None:
        self.titulo_resultado = tk.StringVar(value="Resultados")
        self.mensaje = tk.StringVar(value="La tabla se llenará al calcular.")
        ttk.Label(master, textvariable=self.titulo_resultado,
                  style="Resultado.TLabel", padding=(10, 5)).pack(fill="x", padx=5, pady=(2, 3))
        ttk.Label(master, textvariable=self.mensaje, style="Nota.TLabel",
                  wraplength=660).pack(anchor="w", padx=5, pady=(0, 2))
        fila = ttk.Frame(master)
        fila.pack(side="bottom", fill="x", pady=(4, 0))
        self.exportadores = []
        for nombre, accion in (("CSV", self.exportar_csv), ("PNG", self.exportar_png),
                               ("PDF", self.exportar_pdf)):
            boton = ttk.Button(fila, text=nombre, command=accion, state="disabled", width=5)
            boton.pack(side="left", padx=(0, 3))
            self.exportadores.append(boton)
        self.animadores = []
        for nombre, accion in (("Anterior", lambda: self.avanzar(-1)),
                               ("Siguiente", lambda: self.avanzar(1)),
                               ("Reproducir", self.reproducir), ("Pausar", self.pausar)):
            boton = ttk.Button(fila, text=nombre, command=accion, state="disabled")
            boton.pack(side="left", padx=(0, 2))
            self.animadores.append(boton)
        self.velocidad = tk.DoubleVar(value=3)
        ttk.Label(fila, text="Velocidad").pack(side="left", padx=(5, 2))
        ttk.Scale(fila, from_=1, to=8, variable=self.velocidad, length=63).pack(side="left")
        self.resultados = ttk.Notebook(master)
        self.resultados.pack(fill="both", expand=True)
        self.tablas: dict[str, Tabla] = {}
        self._tabla("Resumen", [])

    def _tabla(self, titulo: str, filas: list[dict]) -> None:
        tabla = Tabla(self.resultados)
        etiqueta = titulo.replace("Trapecio ", "T. ").replace("Simpson 1/3 ", "S. ")
        self.resultados.add(tabla, text=etiqueta)
        tabla.cargar(filas, self.registro.decimales if self.registro else 8, oscuro=self.oscuro)
        self.tablas[titulo] = tabla

    def _actualizar_campos(self, evento: tk.Event | None = None) -> None:
        if evento is not None or self.registro is not None:
            self.pausar()
        campos = {k: v.get() for k, v in self.variables.items()}
        claves = PANELES[self.modulo].visibles(self.metodo.get(), campos, self.comparar.get())
        for clave, marco in self.cajas.items():
            marco.pack_forget()
        if self.tabla_entrada is not None:
            self.datos_marco.pack_forget()
        for clave, marco in self.cajas.items():
            if clave in claves or clave == "decimales":
                marco.pack(fill="x", pady=(0, 3))
        if self.tabla_entrada is not None and (
                self.modulo == "Interpolación" or campos.get("modo") == "Tabla"):
            self.datos_marco.pack(fill="x", pady=(3, 0))
        self.lienzo.yview_moveto(0)

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
        self.mensaje.set("La tabla se llenará al calcular.")
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
        self.ejemplo.set("Seleccionar ejemplo oficial")
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
        self.colores = estilos.aplicar(self.estilo, self.oscuro)
        self.configure(background=self.colores["fondo"])
        self.tema.configure(text="Tema claro" if self.oscuro else "Tema oscuro")
        if self.modulo is None:
            self.inicio()
            return
        self.lienzo.configure(background=self.colores["fondo"])
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
