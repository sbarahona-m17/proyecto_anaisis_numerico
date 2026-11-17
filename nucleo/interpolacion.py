"""Construcción algebraica de interpolantes sin solvers de biblioteca."""
import sympy as sp

from nucleo.resultado import Resultado
from utilidades.parser import compilar
from utilidades.validaciones import nodos, real

X = sp.Symbol("x", real=True)


def _construir(datos: list, evaluaciones: list, metodo: str) -> Resultado:
    puntos = nodos(datos, maximo=25)
    abscisas, ordenadas = zip(*[(sp.Rational(str(x)), sp.Rational(str(y)))
                               for x, y in puntos])
    if not evaluaciones:
        raise ValueError("Ingrese al menos una abscisa de evaluación.")
    consultas = [real(x, "Abscisa de evaluación") for x in evaluaciones]
    componentes, filas, coeficientes = [], [], []
    polinomio = sp.S.Zero
    if metodo == "Lagrange":
        for i, (xi, yi) in enumerate(zip(abscisas, ordenadas)):
            base = sp.prod((X - xj) / (xi - xj)
                           for j, xj in enumerate(abscisas) if i != j)
            polinomio += yi * base
            componentes.append(base)
            filas.append({"i": i, "x": float(xi), "y": float(yi), "Base": str(base)})
    else:
        triangulo = [[yi] for yi in ordenadas]
        for orden in range(1, len(puntos)):
            for i in range(len(puntos) - orden):
                diferencia = triangulo[i + 1][-1] - triangulo[i][-1]
                triangulo[i].append(diferencia / (abscisas[i + orden] - abscisas[i]))
        coeficientes = triangulo[0]
        producto = sp.S.One
        for xi, coeficiente in zip(abscisas, coeficientes):
            polinomio += coeficiente * producto
            componentes.append(polinomio)
            producto *= X - xi
        filas = [{"x": float(xi), **{f"Orden {k}": real(d, "Diferencia dividida")
                                             for k, d in enumerate(fila)}}
                 for xi, fila in zip(abscisas, triangulo)]
    expandido = sp.expand(polinomio)
    aproximar = compilar(polinomio, (X,))
    xs = [x for x, _ in puntos]
    resumen = [{"x*": x, "Resultado": aproximar(x),
                "Extrapolación": "Sí" if not min(xs) <= x <= max(xs) else "No"}
               for x in consultas]
    aviso = ("Hay extrapolación fuera del intervalo de datos."
             if any(f["Extrapolación"] == "Sí" for f in resumen)
             else "Interpolante calculado.")
    return Resultado(resumen[0]["Resultado"], True, aviso, filas,
                     {"resumen": resumen, "puntos": puntos, "componentes": componentes,
                      "expandido": expandido, "Forma del polinomio": str(polinomio),
                      "Polinomio expandido": str(expandido),
                      "Coeficientes": ", ".join(map(str, coeficientes)),
                      "función": aproximar})


def lagrange(datos: list, evaluaciones: list) -> Resultado:
    """Construye las bases cardinales y suma las contribuciones."""
    return _construir(datos, evaluaciones, "Lagrange")


def newton(datos: list, evaluaciones: list) -> Resultado:
    """Construye las diferencias divididas y los polinomios parciales."""
    return _construir(datos, evaluaciones, "Newton")
