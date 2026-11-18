import pytest

from nucleo.derivacion import cinco_puntos
from utilidades.ejemplos import D2
from utilidades.parser import interpretar


@pytest.mark.parametrize("h,d1,d2", [(.5,-.7206978935,-2.8097181764),
                                      (.1,-.7211006241,-2.8098651139),
                                      (.01,-.7211012740,-2.8098653507)])
def test_D1(h, d1, d2):
    r = cinco_puntos(interpretar("20+15sin(x/2)+0.3*x^2"), 4, h)
    assert [f["Resultado"] for f in r.extra["resumen"]] == pytest.approx([d1, d2], abs=5e-10)
    assert [f["Referencia"] for f in r.extra["resumen"]] == pytest.approx(
        [-.7211012741,-2.8098653506], abs=1e-10)
    assert len(r.extra["curva"]) == 8


def test_D2():
    r = cinco_puntos(datos=D2)
    assert [f["Resultado"] for f in r.extra["resumen"]] == [58, 6]
    assert r.tabla[2]["Nodo central"] == "Sí"


def test_D3():
    r = cinco_puntos(interpretar("exp(x)*sin(x)"), 1, .1)
    assert [f["Resultado"] for f in r.extra["resumen"]] == pytest.approx(
        [3.7560993, 2.9374009], abs=5e-8)
    assert [f["Referencia"] for f in r.extra["resumen"]] == pytest.approx(
        [3.7560492, 2.9373879], abs=5e-8)


def test_segunda_derivada_seleccionada_y_referencias_de_valor_absoluto():
    f = interpretar("abs(x)")
    r = cinco_puntos(f, 2, .125, orden=2)
    assert r.valor == 0
    assert [fila["Referencia"] for fila in r.extra["resumen"]] == [1, 0]
    en_cuspide = cinco_puntos(f, 0, .125)
    assert all(fila["Referencia"] is None for fila in en_cuspide.extra["resumen"])
    with pytest.raises(ValueError, match="primera o la segunda"):
        cinco_puntos(f, orden=3)


def test_funcion_fuera_de_dominio_y_tabla_independiente():
    f = interpretar("sqrt(x)")
    with pytest.raises(ValueError, match="real y finita"):
        cinco_puntos(f, .1, .1)
    r = cinco_puntos(f, .1, -1, datos=D2[::-1], orden=2)
    assert r.valor == 6
    assert r.extra["curva"] == []
    assert r.extra["resumen"][1]["Referencia"] is None


@pytest.mark.parametrize("h", [0, -1, float("inf"), 1e-30])
def test_paso_invalido(h):
    with pytest.raises(ValueError):
        cinco_puntos(interpretar("x^2"), 5, h)


def test_nodos_invalidos():
    with pytest.raises(ValueError, match="equiespaciados"):
        cinco_puntos(datos=D2[:-1] + [(4, 700)])
    with pytest.raises(ValueError, match="al menos 5"):
        cinco_puntos(datos=D2[:-1])
