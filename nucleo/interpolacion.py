"""Construcción algebraica de interpolantes sin solvers de biblioteca."""
from fractions import Fraction

import sympy as sp

from nucleo.resultado import Resultado
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
    # Evalúa con los coeficientes racionales antes de redondear el resultado.
    # Así se evitan desbordamientos y cancelaciones en extrapolaciones o nodos cercanos.
    if metodo == "Lagrange":
        pesos = [Fraction(c) for c in sp.Poly(expandido, X).all_coeffs()]
        centros = [Fraction(0)] * (len(pesos) - 1)
    else:
        pesos = [Fraction(c) for c in reversed(coeficientes)]
        centros = [Fraction(x) for x in reversed(abscisas[:-1])]

    def aproximar(x: float) -> float:
        consulta = Fraction(str(real(x, "Abscisa de evaluación")))
        valor = pesos[0]
        for peso, centro in zip(pesos[1:], centros):
            valor = peso + (consulta - centro) * valor
        return real(valor, "Valor interpolado")

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
                      "Coeficientes": ", ".join(map(str, coeficientes)), "Nodos": len(puntos),
                      "función": aproximar})


def lagrange(datos: list, evaluaciones: list) -> Resultado:
    """Construye las bases cardinales y suma las contribuciones."""
    return _construir(datos, evaluaciones, "Lagrange")


def newton(datos: list, evaluaciones: list) -> Resultado:
    """Construye las diferencias divididas y los polinomios parciales."""
    return _construir(datos, evaluaciones, "Newton")
