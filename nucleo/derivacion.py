"""Fórmulas centradas de cinco puntos."""
import sympy as sp

from nucleo.resultado import Resultado
from utilidades.errores import errores
from utilidades.parser import Expresion, compilar
from utilidades.validaciones import (
    Funcion, evaluar, nodos, paso_uniforme, positivo, real, suma_real,
)

PESOS = ((1, -8, 0, 8, -1), (-1, 16, -30, 16, -1))


def _referencia(f: Expresion, x0: float, orden: int) -> tuple[float | None, str]:
    x = f.variables[0]
    punto = sp.Rational(str(x0))
    derivada = sp.diff(f.simbolica, x, orden)
    expresion = str(derivada)
    for valor_absoluto in f.simbolica.atoms(sp.Abs):
        argumento = valor_absoluto.args[0]
        if (argumento.subs(x, punto).is_zero and
                not (argumento.is_nonnegative or argumento.is_nonpositive)):
            return None, expresion
    try:
        return compilar(derivada, f.variables)(x0), expresion
    except ValueError:
        # SymPy puede producir términos como DiracDelta al derivar abs(x).
        # Su sustitución en puntos regulares permite recuperar el valor exacto.
        try:
            return real(derivada.subs(x, punto), "Derivada exacta"), expresion
        except ValueError:
            return None, expresion


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
                 datos: list | None = None, *, orden: int = 1) -> Resultado:
    """Calcula ambas derivadas desde una función o cinco muestras uniformes."""
    if orden not in (1, 2):
        raise ValueError("Seleccione la primera o la segunda derivada.")

    def muestrear(paso: float) -> list:
        xs = [real(x0 + i * paso, "Nodo") for i in range(-2, 3)]
        if len(set(xs)) != 5:
            raise ValueError("El paso es demasiado pequeño para distinguir los nodos.")
        return [(x, evaluar(f, x)) for x in xs]

    if datos is not None:
        puntos = nodos(datos, 5, 5, ordenar=True)
        x0, h = puntos[2][0], paso_uniforme(puntos)
        f = None
    elif f is not None:
        x0, h = real(x0, "Punto central"), positivo(h, "Paso h")
        puntos = muestrear(h)
    else:
        raise ValueError("Ingrese una función o cinco nodos.")
    aproximaciones = _estimar(puntos, h)
    resumen, curva = [], []
    referencias = []
    for grado, aproximacion in enumerate(aproximaciones, 1):
        referencia, expresion = _referencia(f, x0, grado) if isinstance(f, Expresion) else (None, None)
        referencias.append(referencia)
        resumen.append({"Magnitud": f"Derivada de orden {grado}", "Resultado": aproximacion,
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
    return Resultado(aproximaciones[orden - 1], True, "Primera y segunda derivada calculadas.",
                     filas, {"resumen": resumen, "curva": curva, "puntos": puntos,
                             "función": f, "h": h, "x₀": x0, "Nodos": len(puntos)})
