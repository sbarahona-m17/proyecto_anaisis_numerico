"""Pruebas de integración con widgets y figuras Tk reales."""
import time
import tkinter as tk
from tkinter import ttk

import pytest

from interfaz.panel_ayuda import TEORIA, abrir
from interfaz.ventana_principal import Aplicacion
from utilidades.comparaciones import METODOS
from utilidades.ejemplos import EJEMPLOS


@pytest.fixture(scope="module")
def ventana_tk():
    try:
        ventana = Aplicacion()
    except tk.TclError as error:
        pytest.skip(f"Tk no dispone de pantalla: {error}")
    ventana.update()
    yield ventana
    ventana.destroy()


@pytest.fixture
def app(ventana_tk, monkeypatch):
    ventana = ventana_tk
    ventana.inicio()
    ventana.historial.clear()
    if ventana.oscuro:
        ventana.alternar_tema()
    dialogos = []
    monkeypatch.setattr("interfaz.ventana_principal.messagebox.showerror",
                        lambda titulo, detalle, **kw: dialogos.append((titulo, detalle)))
    ventana.dialogos_prueba = dialogos
    ventana.update()
    return ventana


def _esperar(app):
    limite = time.monotonic() + 15
    while app.boton_calcular.instate(["disabled"]) and time.monotonic() < limite:
        app.update()
        time.sleep(.02)
    app.update()
    assert not app.boton_calcular.instate(["disabled"])


@pytest.mark.parametrize("modulo", list(EJEMPLOS))
def test_calculo_comparacion_y_pestanas(app, modulo):
    app.abrir_modulo(modulo)
    app.ejemplo.set(next(iter(EJEMPLOS[modulo])))
    app.cargar_ejemplo()
    app.comparar.set(True)
    app._actualizar_campos()
    app.boton_calcular.invoke()
    _esperar(app)
    assert not app.dialogos_prueba
    assert app.registro.calculo.comparacion
    assert all(r.convergio for r in app.registro.calculo.resultados.values())
    assert app.tablas["Resumen"].filas
    for pestana in app.graficas.libro.tabs():
        app.graficas.libro.select(pestana)
        app.update()
        figura = app.graficas.figura()
        assert figura.axes[0].get_title()
        assert figura.axes[0].get_xlabel()
        assert figura.axes[0].get_ylabel()
    alto = app.graficas.winfo_height()
    assert alto >= 180
    app.alternar_tema()
    app.avanzar(1)
    assert app.graficas.paso == 0
    app.avanzar(1)
    assert app.graficas.paso == 1
    app.reproducir()
    app.pausar()
    assert app.reloj is None
    app.volver()
    assert app.registro is None
    assert app.modulo == modulo
    app.volver()
    assert app.modulo is None


@pytest.mark.parametrize("modulo,metodo,esperado,tolerancia", [
    ("Raíces", "Bisección", 2.0945514815, 1e-6),
    ("Raíces", "Falsa posición", 2.0945514815, 1e-6),
    ("Raíces", "Newton-Raphson", 2.0945514815, 1e-6),
    ("Raíces", "Secante", 2.0945514815, 1e-6),
    ("Diferenciación", "Primera derivada", -.7206978935, 5e-10),
    ("Diferenciación", "Segunda derivada", -2.8097181764, 5e-10),
    ("Interpolación", "Lagrange", 439.047619, 5e-7),
    ("Interpolación", "Newton", 439.047619, 5e-7),
    ("Integración", "Trapecio simple", .750000000, 5e-10),
    ("Integración", "Trapecio compuesto", .782794118, 5e-10),
    ("Integración", "Simpson 1/3 simple", .783333333, 5e-10),
    ("Integración", "Simpson 1/3 compuesto", .785392157, 5e-10),
    ("EDO", "Euler", 679.0270, 5e-5),
    ("EDO", "Heun", 733.4076, 5e-5),
    ("EDO", "Runge-Kutta 4", 741.8001, 5e-5),
], ids=[metodo for nombres in METODOS.values() for metodo in nombres])
def test_calcular_cada_metodo_desde_su_pantalla(app, modulo, metodo, esperado, tolerancia):
    app.abrir_modulo(modulo)
    app.ejemplo.set(next(iter(EJEMPLOS[modulo])))
    app.cargar_ejemplo()
    app.metodo.set(metodo)
    app._actualizar_campos()
    app.boton_calcular.invoke()
    _esperar(app)

    assert not app.dialogos_prueba
    assert list(app.registro.calculo.resultados) == [metodo]
    r = app.registro.calculo.resultados[metodo]
    assert r.convergio and r.valor == pytest.approx(esperado, abs=tolerancia)
    assert app.tablas[metodo].filas == r.tabla
    assert metodo in app.titulo_resultado.get()
    assert app.graficas.figura().axes[0].get_title()
    assert all(boton.instate(["!disabled"]) for boton in app.exportadores)


def test_diferenciacion_importa_csv_y_traza_la_tangente_de_primera_derivada(app, tmp_path, monkeypatch):
    csv = tmp_path / "muestras.csv"
    csv.write_text("x,y\n0,0\n1,1\n2,4\n3,9\n4,16", encoding="utf-8")
    monkeypatch.setattr("interfaz.ventana_principal.filedialog.askopenfilename", lambda **_: str(csv))
    app.abrir_modulo("Diferenciación")
    app.variables["modo"].set("Tabla")
    app.metodo.set("Segunda derivada")
    app._actualizar_campos()
    app.importar()
    app.boton_calcular.invoke()
    _esperar(app)

    assert not app.dialogos_prueba
    assert [fila["Resultado"] for fila in app.registro.calculo.resumen] == [4, 2]
    figura = app.graficas.figura()
    tangente, = figura.axes[0].lines
    assert tangente.get_ydata().tolist() == [-4, 0, 4, 8, 12]
    _, _, barra, _ = app.graficas.figuras[app.graficas.libro.select()]
    barra.pan()
    assert barra.mode.name == "PAN"
    barra.zoom()
    assert barra.mode.name == "ZOOM"
    barra.zoom()
    assert barra.mode.name == "NONE"


def test_cambiar_metodo_y_vista_mantiene_entradas_y_muestra_su_resultado(app):
    app.abrir_modulo("Raíces")
    botones = [control for marco in app.cuerpo.winfo_children()
               for control in marco.winfo_children() if isinstance(control, ttk.Radiobutton)]
    assert [boton["text"] for boton in botones] == list(METODOS["Raíces"])
    assert botones[0].instate(["selected"])
    app.variables["f"].set("x^2-4")
    app.variables["x0"].set("3")
    botones[2].invoke()
    assert botones[2].instate(["selected"])
    app.boton_calcular.invoke()
    _esperar(app)
    assert app.registro.calculo.resultados["Newton-Raphson"].valor == pytest.approx(2)

    titulo = app.titulo_resultado.get()
    app.vistas_trabajo.select(app.resultados)
    app.update()
    assert app.resultados.winfo_ismapped() and not app.graficas.winfo_ismapped()
    assert app.titulo_resultado.get() == titulo
    app.vistas_trabajo.select(app.graficas)
    app.update()
    assert app.graficas.winfo_ismapped() and not app.resultados.winfo_ismapped()
    assert app.graficas.figura().axes[0].has_data()

    botones[0].invoke()
    assert app.variables["f"].get() == "x^2-4"
    assert app.registro is None
    assert all(boton.instate(["disabled"]) for boton in app.exportadores)


def test_importar_editar_exportar_y_recuperar(app, tmp_path, monkeypatch):
    entrada = tmp_path / "entrada.csv"
    entrada.write_text("x,y\n0,2\n1,3\n2,6", encoding="utf-8")
    monkeypatch.setattr("interfaz.ventana_principal.filedialog.askopenfilename",
                        lambda **kw: str(entrada))
    monkeypatch.setattr("interfaz.ventana_principal.filedialog.asksaveasfilename",
                        lambda **kw: str(tmp_path / ("reporte" + kw["defaultextension"])))
    app.abrir_modulo("Interpolación")
    app.importar()
    app.update()
    app.tabla_entrada._abrir("0", "#2")
    editor = app.tabla_entrada.editor
    assert editor is not None
    editor.delete(0, "end")
    editor.insert(0, "5")
    app.tabla_entrada.confirmar()
    app.variables["consultas"].set("0 1")
    app.ejecutar()
    _esperar(app)
    for exportar in (app.exportar_csv, app.exportar_png, app.exportar_pdf):
        exportar()
    assert not app.dialogos_prueba
    assert "5.0" in (tmp_path / "reporte.csv").read_text(encoding="utf-8-sig")
    assert (tmp_path / "reporte.png").read_bytes().startswith(b"\x89PNG")
    assert (tmp_path / "reporte.pdf").read_bytes().startswith(b"%PDF-")
    app.limpiar()
    assert not app.tabla_entrada.datos()
    app.abrir_historial()
    ventana = next(w for w in app.winfo_children() if isinstance(w, tk.Toplevel))
    tabla, boton = ventana.winfo_children()
    tabla.arbol.selection_set("0")
    boton.invoke()
    assert app.registro.calculo.resumen[0]["Resultado"] == 5


def test_opciones_adicionales_se_pliegan_y_conservan_sus_valores(app):
    app.abrir_modulo("Raíces")
    app.update()
    assert app.cajas["tol"].winfo_ismapped()
    assert not app.cajas["decimales"].winfo_ismapped()
    app.boton_opciones.invoke()
    app.update()
    assert app.cajas["decimales"].winfo_ismapped()
    assert app.cajas["referencia"].winfo_ismapped()
    app.variables["decimales"].set("5")
    app.boton_opciones.invoke()
    app.update()
    assert not app.cajas["decimales"].winfo_ismapped()
    app.boton_calcular.invoke()
    _esperar(app)
    assert not app.dialogos_prueba
    assert app.registro.decimales == 5


def test_ayuda_general_y_metodos(app):
    assert {m for nombres in METODOS.values() for m in nombres} == set(TEORIA)
    for metodo in (None, "Bisección"):
        abrir(app, app.colores, metodo)
        app.update()
        ventana = next(w for w in app.winfo_children() if isinstance(w, tk.Toplevel))
        assert (metodo or "Ayuda general") in ventana.title()
        ventana.destroy()


def test_catalogo_completo(app):
    for modulo, ejemplos in EJEMPLOS.items():
        app.abrir_modulo(modulo)
        for clave, ejemplo in ejemplos.items():
            app.ejemplo.set(clave)
            app.cargar_ejemplo()
            for campo, dato in ejemplo.items():
                if campo in app.variables:
                    assert app.variables[campo].get() == str(dato)
                elif campo == "metodo":
                    assert app.metodo.get() == dato
                elif campo == "datos":
                    assert app.tabla_entrada.datos() == [tuple(map(str, fila)) for fila in dato]


def test_entrada_invalida_y_recuperacion(app):
    app.abrir_modulo("Raíces")
    app.ejemplo.set(next(e for e in EJEMPLOS["Raíces"] if e.startswith("R-4a")))
    app.cargar_ejemplo()
    app.ejecutar()
    _esperar(app)
    assert "cambio de signo" in app.dialogos_prueba[0][1]
    app.ejemplo.set(next(e for e in EJEMPLOS["Raíces"] if e.startswith("R-3")))
    app.cargar_ejemplo()
    app.ejecutar()
    _esperar(app)
    assert app.registro.calculo.resumen[0]["Resultado"] == 6
