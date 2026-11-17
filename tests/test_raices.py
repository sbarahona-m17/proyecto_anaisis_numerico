import pytest

from nucleo import raices
from nucleo.resultado import Resultado
from utilidades.parser import interpretar


@pytest.mark.parametrize("texto,a,b,x0,esperada,iteraciones", [
    ("x^3-2x-5", 2, 3, 2.5, 2.0945514815, [20, 13, 5, 6]),
    ("exp(-x)-x", 0, 1, .5, .5671432904, [20, 7, 3, 5]),
    ("1/(0.1+0.9/x)-4", 2, 10, 3, 6, [1, 13, 5, 6]),
], ids=["R-1", "R-2", "R-3"])
def test_oficiales(texto, a, b, x0, esperada, iteraciones):
    f = interpretar(texto)
    resultados = [raices.biseccion(f, a, b), raices.falsa_posicion(f, a, b),
                  raices.newton(f, x0), raices.secante(f, a, b)]
    for r, n in zip(resultados, iteraciones):
        assert isinstance(r, Resultado)
        assert r.convergio
        assert r.valor == pytest.approx(esperada, abs=1e-6)
        assert abs(len(r.tabla) - n) <= 1
    if esperada == 6:
        assert resultados[0].valor == 6
        assert len(resultados[0].tabla) == 1
        assert resultados[0].tabla[0]["f(c)"] == 0


def test_R4():
    with pytest.raises(ValueError, match="cambio de signo"):
        raices.biseccion(interpretar("x^2+1"), -1, 1)
    f = interpretar("x^3-2x+2")
    assert "ciclo" in raices.newton(f, 0).mensaje
    assert not raices.newton(f, 0).convergio
    assert raices.newton(f, -2).valor == pytest.approx(-1.769292, abs=1e-6)
    assert "Derivada nula" in raices.newton(interpretar("x^2-4"), 0).mensaje


def test_fronteras():
    assert raices.biseccion(lambda x: x, 0, 1).valor == 0
    assert raices.secante(lambda x: 1, 0, 1).convergio is False
    r = raices.biseccion(lambda x: x*x-2, 0, 2, max_iter=1)
    assert not r.convergio and "máximo" in r.mensaje
    assert raices.biseccion(lambda x: x*x-2, 0, 2, criterio="Relativo (%)").convergio
    assert raices.biseccion(lambda x: x*x-2, 0, 2, criterio="Residuo").convergio


@pytest.mark.parametrize("opciones", [{"tol": 0}, {"tol": -1}, {"max_iter": 0},
                                     {"max_iter": 2.5}, {"criterio": "otro"}])
def test_parametros_invalidos(opciones):
    with pytest.raises(ValueError):
        raices.biseccion(lambda x: x, -1, 1, **opciones)
