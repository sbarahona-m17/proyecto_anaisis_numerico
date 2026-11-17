"""Pruebas de integración con widgets y figuras Tk reales."""
import time
import tkinter as tk

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
