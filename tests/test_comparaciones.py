from utilidades.comparaciones import calcular
import pytest

from utilidades.ejemplos import D2, I2, N3


def test_interpolantes_equivalentes():
    c = calcular("Interpolación", "Newton", {"consultas": "2.5, 8"}, I2, True)
    assert "verificada" in c.detalles
    assert len(c.resumen) == 6


def test_comparacion_raices_a_isla_fallos():
    c = calcular("Raíces", "Bisección", dict(f="x^2-4", a=3, b=4, x0=0,
                 s0=1, s1=3, tol=1e-6, max_iter=100, criterio="Absoluto"), [], True)
    assert not c.resultados["Newton-Raphson"].convergio
    assert not c.resultados["Falsa posición"].convergio
    assert c.resultados["Secante"].convergio


def test_refinamiento_edo():
    c = calcular("EDO", "Euler", dict(f="y", exacta="exp(t)", t0=0, tf=1, y0=1,
                 h=.1, n=10, paso="Tamaño de paso h"), [], True)
    for fila in c.resumen:
        assert fila["Error con h/2"] < fila["Error absoluto"]
        assert fila["Pasos con h/2"] == 20


def test_comparacion_mantiene_separado_el_error_relativo_de_la_raiz():
    c = calcular("Raíces", "Bisección", dict(f="x^2-4", a=0, b=3, tol=.1,
                 max_iter=100, criterio="Absoluto", referencia=2), [])
    fila = c.resumen[0]
    assert fila["Error relativo (%)"] == pytest.approx(100 * abs(fila["Resultado"] - 2) / 2)
    assert fila["Cambio relativo (%)"] == c.resultados["Bisección"].tabla[-1]["Error relativo (%)"]
    assert fila["Error relativo (%)"] != fila["Cambio relativo (%)"]


def test_comparaciones_con_datos_tabulares():
    d = calcular("Diferenciación", "Segunda derivada",
                 {"modo": "Tabla", "x0": "", "h": ""}, D2, True)
    assert [(fila["Método"], fila["Resultado"]) for fila in d.resumen] == [
        ("Primera derivada", 58), ("Segunda derivada", 6)]
    q = calcular("Integración", "Trapecio compuesto",
                 {"modo": "Tabla", "a": "", "b": "", "n": "", "unidad": "Minutos y Mbps"},
                 N3, True)
    assert q.resultados["Simpson 1/3 compuesto"].valor == 830000
    assert all("Diferencia vs. trapecio simple" in fila for fila in q.resumen)
