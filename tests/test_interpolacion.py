import pytest

from nucleo import interpolacion
from utilidades.ejemplos import I1, I2


@pytest.mark.parametrize("datos,x,esperada,coeficientes", [
    (I1, 6, 439.047619, [120,90,-6.666667,.059524]),
    (I2, 2.5, 97.628571, [42,26,0,2.2,-.438095]),
], ids=["I-1", "I-2"])
def test_oficiales(datos, x, esperada, coeficientes):
    lag, new = [f(datos, [x]) for f in (interpolacion.lagrange, interpolacion.newton)]
    assert lag.extra["expandido"] == new.extra["expandido"]
    assert [lag.valor, new.valor] == pytest.approx([esperada]*2, abs=5e-7)
    assert list(new.tabla[0].values())[1:] == pytest.approx(coeficientes, abs=5e-7)


@pytest.mark.parametrize("metodo", [interpolacion.lagrange, interpolacion.newton])
def test_fronteras(metodo):
    with pytest.raises(ValueError, match="distintas"):
        metodo([(1, 2), (1, 3)], [2])
    r = metodo([(1, 2), (2, 3)], [1, 3])
    assert r.valor == 2
    assert "extrapolación" in r.mensaje
