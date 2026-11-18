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


@pytest.mark.parametrize("escala", [1, 1e-100])
def test_falsa_posicion_no_confunde_paso_pequeno_con_raiz(escala):
    r = raices.falsa_posicion(lambda x: escala * (x**10 - 1), 0, 100, max_iter=10)
    assert not r.convergio
    assert r.extra["Iteraciones"] == 10
    assert r.extra["Cambio absoluto"] < 1e-6
    assert r.extra["Residuo"] == pytest.approx(escala, abs=0)


def test_secante_no_acepta_un_paso_pequeno_si_no_hay_cambio_en_f():
    r = raices.secante(lambda x: x**10 - 1, 100, 0)
    assert not r.convergio
    assert r.extra["Cambio absoluto"] < 1e-6
    assert "Denominador nulo" in r.mensaje


def test_newton_y_secante_con_f_escalada():
    n = raices.newton(interpretar("1e-20*(x-2)"), 1)
    assert n.convergio and n.valor == 2
    assert n.extra["Derivada simbólica"]
    assert n.tabla[0]["Ea"] == 1
    assert n.tabla[0]["Error relativo (%)"] == 50

    s = raices.secante(lambda x: 1e308 * x, -1, 1)
    assert s.convergio and s.valor == 0
    assert s.tabla[0]["Ea"] == 1
    assert s.tabla[0]["Error relativo (%)"] is None


def test_dominio_invalido_y_perdida_de_dominio_en_newton():
    f = interpretar("log(x)")
    with pytest.raises(ValueError, match="real y finita"):
        raices.falsa_posicion(f, -1, 2)
    r = raices.newton(f, 4)
    assert not r.convergio and r.valor == 4
    assert "real y finita" in r.mensaje


@pytest.mark.parametrize("opciones", [{"tol": 0}, {"tol": -1}, {"max_iter": 0},
                                     {"max_iter": 2.5}, {"criterio": "otro"}])
def test_parametros_invalidos(opciones):
    with pytest.raises(ValueError):
        raices.biseccion(lambda x: x, -1, 1, **opciones)
