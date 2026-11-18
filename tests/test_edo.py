import pytest

from nucleo.edo import METODOS, resolver
from utilidades.parser import interpretar


@pytest.mark.parametrize("metodo,esperados,error_final", list(zip(METODOS, [
    [50,94.6956,173.9267,302.5381,481.8288,679.0270],
    [50,103.6413,202.9786,360.1233,554.7591,733.4076],
    [50,104.8438,206.7568,367.1139,563.4975,741.8001],
], [62.8144, 8.4337, .0412])))
def test_E1(metodo, esperados, error_final):
    f = interpretar("0.8y(1-y/1000)", ("t", "y"))
    ex = interpretar("1000/(1+19*exp(-0.8*t))", ("t",))
    r = resolver(metodo, f, 0, 50, 5, h=.5, exacta=ex)
    assert r.convergio
    assert [f["y"] for f in r.tabla[::2]] == pytest.approx(esperados, abs=5e-5)
    assert [f["Referencia"] for f in r.tabla[::2]] == pytest.approx(
        [50, 104.8520, 206.7810, 367.1556, 563.5448, 741.8413], abs=5e-5)
    assert r.extra["Error absoluto"] == pytest.approx(error_final, abs=5e-5)


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


def test_etapas_de_heun_y_rk4():
    def f(t, y):
        return y

    heun = resolver("Heun", f, 0, 1, .25, n=1)
    rk4 = resolver("Runge-Kutta 4", f, 0, 1, .25, n=1)
    assert heun.tabla[-1]["Predictor"] == 1.25
    assert heun.tabla[-1]["Corrector"] == 1.28125
    assert [rk4.tabla[-1][f"k{i}"] for i in range(1, 5)] == [1, 1.125, 1.140625, 1.28515625]


def test_edo_conserva_pasos_completados_si_sale_del_dominio():
    f = interpretar("sqrt(.5-t)", ("t", "y"))
    r = resolver("Euler", f, 0, 0, 1, n=4)
    assert not r.convergio
    assert r.extra["Pasos"] == 3
    assert r.extra["Tiempo alcanzado"] == .75
    assert r.valor == r.tabla[-1]["y"]
    assert "real y finita" in r.mensaje


def test_referencia_debe_satisfacer_la_edo_y_la_condicion_inicial():
    f = interpretar("y", ("t", "y"))
    with pytest.raises(ValueError, match="condición inicial"):
        resolver("Euler", f, 0, 1, 1, n=2, exacta=interpretar("2*exp(t)", ("t",)))
    with pytest.raises(ValueError, match="no satisface la EDO"):
        resolver("Euler", f, 0, 1, 1, n=2, exacta=interpretar("1+t", ("t",)))


@pytest.mark.parametrize("parametros", [{"h": 0}, {"h": -1}, {"n": 0}, {"n": 2.5}, {"h": 1, "n": 1}])
def test_paso_invalido(parametros):
    with pytest.raises(ValueError):
        resolver("Euler", lambda t, y: 1, 0, 0, 1, **parametros)
