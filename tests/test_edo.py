import pytest

from nucleo.edo import METODOS, resolver
from utilidades.parser import interpretar


@pytest.mark.parametrize("metodo,esperados", list(zip(METODOS, [
    [50,94.6956,173.9267,302.5381,481.8288,679.0270],
    [50,103.6413,202.9786,360.1233,554.7591,733.4076],
    [50,104.8438,206.7568,367.1139,563.4975,741.8001],
])))
def test_E1(metodo, esperados):
    f = interpretar("0.8y(1-y/1000)", ("t", "y"))
    ex = interpretar("1000/(1+19*exp(-0.8*t))", ("t",))
    r = resolver(metodo, f, 0, 50, 5, h=.5, exacta=ex)
    assert r.convergio
    assert [f["y"] for f in r.tabla[::2]] == pytest.approx(esperados, abs=5e-5)
    assert r.extra["Referencia"] == pytest.approx(741.8413, abs=5e-5)


@pytest.mark.parametrize("metodo,esperado", list(zip(METODOS, [4.865785, 5.233055, 5.305363])))
def test_E2(metodo, esperado):
    f = interpretar("y-t^2+1", ("t", "y"))
    ex = interpretar("(t+1)^2-0.5*exp(t)", ("t",))
    r = resolver(metodo, f, 0, .5, 2, h=.2, exacta=ex)
    assert r.valor == pytest.approx(esperado, abs=5e-7)
    assert r.extra["Referencia"] == pytest.approx(5.305472, abs=5e-7)


def test_ajuste_y_fallo():
    f = lambda t, y: 1
    r = resolver("Euler", f, 0, 0, 1, h=.3)
    assert r.tabla[-1]["t"] == 1
    assert r.tabla[-1]["Paso"] == pytest.approx(.1)
    assert "acortado" in r.mensaje
    assert resolver("Heun", f, 0, 0, 1, n=3).valor == 1
    assert not resolver("Euler", lambda t, y: 1e308, 0, 1e308, 2, n=1).convergio


@pytest.mark.parametrize("parametros", [{"h": 0}, {"h": -1}, {"n": 0}, {"n": 2.5}, {"h": 1, "n": 1}])
def test_paso_invalido(parametros):
    with pytest.raises(ValueError):
        resolver("Euler", lambda t, y: 1, 0, 0, 1, **parametros)
