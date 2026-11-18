"""Reglas de Newton–Cotes de dos y tres nodos."""
from math import isfinite

from nucleo.resultado import Resultado
from utilidades.errores import errores
from utilidades.parser import Expresion
from utilidades.referencia_integral import referencia_integral
from utilidades.validaciones import (
    Funcion, entero, evaluar, nodos, paso_uniforme, positivo, real, suma_real,
)

METODOS = ("Trapecio simple", "Trapecio compuesto",
           "Simpson 1/3 simple", "Simpson 1/3 compuesto")


def integrar(metodo: str, f: Funcion | None = None, a: float = 0, b: float = 1,
             n: int = 4, datos: list | None = None, transferencia: bool = False,
             referencia: bool = True) -> Resultado:
    """Integra una función o nodos equiespaciados con la regla elegida."""
    if metodo not in METODOS:
        raise ValueError("Seleccione una regla de integración válida.")
    simpson = metodo.startswith("Simpson")
    simple = metodo.endswith("simple")
    fijo = 2 if simpson else 1
    if datos is not None:
        f = None
        puntos = nodos(datos, ordenar=True)
        n = len(puntos) - 1
        if simple and n != fijo:
            # Las reglas simples usan los extremos y Simpson usa el punto medio medido.
            if simpson and n % 2:
                raise ValueError("Simpson simple necesita un nodo exactamente en el punto medio.")
            paso_uniforme(puntos)
            puntos = [puntos[0], puntos[n // 2], puntos[-1]] if simpson else [puntos[0], puntos[-1]]
            n = fijo
        h = paso_uniforme(puntos)
    else:
        if f is None:
            raise ValueError("Ingrese una función o datos tabulados.")
        a, b = real(a, "Límite a"), real(b, "Límite b")
        if a >= b:
            raise ValueError("El límite inferior debe ser menor que el superior.")
        n = fijo if simple else entero(n, "Número de subintervalos")
        if simpson and n % 2:
            raise ValueError("Simpson compuesto exige un número par de subintervalos.")
        amplitud = b - a
        amplitud_finita = isfinite(amplitud)
        h = positivo(amplitud / n if amplitud_finita else b / n - a / n, "Paso")
        xs = [a]
        for i in range(1, n):
            fraccion = i / n
            x = a + amplitud * fraccion if amplitud_finita else (1 - fraccion) * a + fraccion * b
            xs.append(x)
        xs.append(b)
        if any(x >= siguiente for x, siguiente in zip(xs, xs[1:])):
            raise ValueError("El paso es demasiado pequeño para distinguir los nodos.")
        puntos = [(x, evaluar(f, x)) for x in xs]
    if simpson and n % 2:
        raise ValueError("Simpson compuesto exige un número par de subintervalos.")
    escala = 60 if transferencia else 1
    paso = positivo(h * escala, "Paso efectivo")
    filas = []
    for i, (x, y) in enumerate(puntos):
        peso = 1 if i in (0, n) else 4 if simpson and i % 2 else 2
        fila = {"i": i, "x": x}
        if transferencia:
            fila["Tiempo (s)"] = real(x * escala, "Tiempo en segundos")
        filas.append({**fila, "f(x)": y, "Peso": peso, "Peso × f(x)": peso * y})
    divisor = 3 if simpson else 2
    try:
        suma = suma_real((fila["Peso × f(x)"] for fila in filas), "Suma ponderada")
        valor = real((suma / divisor) * paso, "Integral")
    except ValueError:
        # Con pasos pequeños, el área puede caber aunque la suma ponderada desborde.
        if paso >= 1:
            raise
        valor = suma_real(((fila["f(x)"] * paso) * (fila["Peso"] / divisor)
                           for fila in filas), "Integral")
    exacta, expresion = None, None
    if referencia and datos is None and isinstance(f, Expresion):
        exacta, expresion = referencia_integral(f.simbolica, f.variables[0], a, b)
        if exacta is not None and transferencia:
            exacta = real(exacta * escala, "Integral de referencia")
            expresion = f"{escala} × ({expresion})"
    extra = {"puntos": puntos, "función": f, "Subintervalos": n,
             "Paso efectivo": paso, "Referencia": exacta,
             "Referencia simbólica": expresion,
             **errores(valor, exacta)}
    if transferencia:
        extra.update({"Volumen (GB)": valor / 8000, "Unidad": "Mb",
                      "Conversión": "x en minutos, paso en segundos; 1 GB = 8000 Mb"})
    return Resultado(valor, True, "Cuadratura completada.", filas, extra)
