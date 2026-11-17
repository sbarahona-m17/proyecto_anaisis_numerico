import math

import pytest

from utilidades.parser import interpretar


@pytest.mark.parametrize("texto,x,resultado", [
    ("x^3-2x-5", 2, -1), ("20+15sin(x/2)", 0, 20), ("e^(-x)", 1, math.exp(-1)),
    ("ln(x)+2", 1, 2), ("-x^2", 2, -4), ("2^3^2", 0, 512),
    ("sqrt(x)+abs(-x)+pi", 4, 6+math.pi), ("1e-6*x", 2, 2e-6),
])
def test_gramatica(texto, x, resultado):
    assert interpretar(texto)(x) == pytest.approx(resultado)


@pytest.mark.parametrize("texto", ["", "x.foo", "__import__('os')", "cbrt(x)", "t", "x+",
                                   "sin()", "x//2", "x^", "x**2", "sin(x,2)", "NaN", "inf"])
def test_rechazo(texto):
    with pytest.raises(ValueError):
        interpretar(texto)


@pytest.mark.parametrize("texto,x", [("log(x)", -1), ("sqrt(x)", -1), ("1/x", 0),
                                    ("0*log(x)", -1), ("exp(x)", 1000)])
def test_dominio(texto, x):
    with pytest.raises(ValueError, match="real y finita"):
        interpretar(texto)(x)
