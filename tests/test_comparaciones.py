from utilidades.comparaciones import calcular
from utilidades.ejemplos import I2


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
