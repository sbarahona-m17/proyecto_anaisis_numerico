"""Fórmulas centradas de cinco puntos."""
import sympy as sp

from nucleo.resultado import Resultado
from utilidades.errores import errores
from utilidades.parser import Expresion
from utilidades.validaciones import (
    Funcion, evaluar, nodos, paso_uniforme, positivo, real, suma_real,
)

PESOS = ((1, -8, 0, 8, -1), (-1, 16, -30, 16, -1))


def _estimar(puntos: list, h: float) -> tuple[float, float]:
    valores = [y for _, y in puntos]
    centro = valores[2]
    denominadores = (12 * h, 12 * h * h)
    if any(d == 0 for d in denominadores):
        raise ValueError("El paso es demasiado pequeño para representar el denominador.")
    return tuple(real(suma_real((c * (y - centro) for c, y in zip(pesos, valores)), "Numerador")
                      / real(d, "Denominador"), "Derivada")
                 for d, pesos in zip(denominadores, PESOS))


def cinco_puntos(f: Funcion | None = None, x0: float = 0.0, h: float = 0.1,
                 datos: list | None = None) -> Resultado:
    """Calcula ambas derivadas desde una función o cinco muestras uniformes."""
    def muestrear(paso: float) -> list:
        xs = [real(x0 + i * paso, "Nodo") for i in range(-2, 3)]
        if len(set(xs)) != 5:
            raise ValueError("El paso es demasiado pequeño para distinguir los nodos.")
        return [(x, evaluar(f, x)) for x in xs]

    if datos is not None:
        puntos = nodos(datos, 5, 5, ordenar=True)
        x0, h = puntos[2][0], paso_uniforme(puntos)
    elif f is not None:
        x0, h = real(x0, "Punto central"), positivo(h, "Paso h")
        puntos = muestrear(h)
    else:
        raise ValueError("Ingrese una función o cinco nodos.")
    aproximaciones = _estimar(puntos, h)
    resumen, curva = [], []
    referencias = []
    for orden, aproximacion in enumerate(aproximaciones, 1):
        referencia, expresion = None, None
        if isinstance(f, Expresion):
            try:
                derivada = f.derivada(orden)
                expresion = str(derivada.simbolica)
                referencia = derivada(x0)
                for valor_absoluto in f.simbolica.atoms(sp.Abs):
                    argumento = valor_absoluto.args[0].subs(f.variables[0], x0)
                    if argumento.is_zero:
                        referencia = None
                        break
            except ValueError:
                referencia = None
        referencias.append(referencia)
        resumen.append({"Magnitud": f"Derivada de orden {orden}", "Resultado": aproximacion,
                        "Referencia": referencia, "Expresión exacta": expresion,
                        **errores(aproximacion, referencia)})
    if f is not None and any(v is not None for v in referencias):
        for k in range(1, 9):
            paso = 10.0**-k
            try:
                estimaciones = _estimar(muestrear(paso), paso)
            except (ArithmeticError, ValueError):
                continue
            curva.append((paso, *(errores(v, r)["Error absoluto"]
                                   for v, r in zip(estimaciones, referencias))))
    filas = [{"x": x, "f(x)": y, "Peso primera": p, "Peso segunda": s,
              "Nodo central": "Sí" if i == 2 else ""}
             for i, ((x, y), p, s) in enumerate(zip(puntos, *PESOS))]
    return Resultado(aproximaciones[0], True, "Primera y segunda derivada calculadas.",
                     filas, {"resumen": resumen, "curva": curva, "puntos": puntos,
                             "función": f, "h": h, "x₀": x0})
