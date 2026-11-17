import pytest

from nucleo.integracion import METODOS, integrar
from utilidades.ejemplos import N3
from utilidades.parser import interpretar


@pytest.mark.parametrize("i,n,n1,n2", [
    (0, 1, .750000000, 2116.118980), (2, 2, .783333333, 2295.725388),
    (1, 4, .782794118, 2292.565221), (3, 4, .785392157, 2306.479033),
    (1, 10, .784981497, None), (3, 10, .785398153, None),
    (1, 8, None, 2303.617530), (3, 8, None, 2307.301634),
])
def test_N1_N2(i, n, n1, n2):
    for f, b, esperado, referencia, tol in [
        ("1/(1+x^2)", 1, n1, .785398163, 5e-10),
        ("250+40*x*exp(-0.3*x)", 8, n2, 2307.359537, 5e-7),
    ]:
        if esperado is not None:
            r = integrar(METODOS[i], interpretar(f), 0, b, n)
            assert r.valor == pytest.approx(esperado, abs=tol)
            assert r.extra["Referencia"] == pytest.approx(referencia, abs=tol)


@pytest.mark.parametrize("i,mb,gb", [(1, 825000, 103.125), (3, 830000, 103.75)])
def test_N3(i, mb, gb):
    r = integrar(METODOS[i], datos=N3, transferencia=True)
    assert r.valor == mb
    assert r.extra["Volumen (GB)"] == gb


@pytest.mark.parametrize("a,b,n", [(0, 1, 3), (0, 1, 0), (2, 1, 4), (1, 1, 4)])
def test_simpson_invalido(a, b, n):
    with pytest.raises(ValueError):
        integrar(METODOS[3], interpretar("x"), a, b, n)


def test_dominio_y_nodos():
    with pytest.raises(ValueError, match="finita"):
        integrar(METODOS[0], interpretar("log(x)"), -1, 1)
    with pytest.raises(ValueError, match="equiespaciados"):
        integrar(METODOS[1], datos=[(0, 1), (1, 2), (3, 3)])
