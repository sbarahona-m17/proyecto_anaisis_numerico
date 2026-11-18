"""Validaciones comunes de entradas y evaluaciones."""
from collections.abc import Callable, Iterable
from math import fsum, isclose, isfinite
import re

Funcion = Callable[..., float]


def real(valor: object, nombre: str) -> float:
    """Convierte a real finito o produce un mensaje contextual."""
    try:
        numero = float(valor)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{nombre} debe ser un número real.") from None
    if not isfinite(numero):
        raise ValueError(f"{nombre} debe ser finito.")
    return numero


def positivo(valor: object, nombre: str) -> float:
    numero = real(valor, nombre)
    if numero <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero.")
    return numero


def entero(valor: object, nombre: str, minimo: int = 1,
           maximo: int = 10000) -> int:
    texto = str(valor).strip()
    if not re.fullmatch(r"[+-]?[0-9]{1,10}", texto):
        raise ValueError(f"{nombre} debe ser un entero.")
    numero = int(texto)
    if not minimo <= numero <= maximo:
        raise ValueError(f"{nombre} debe estar entre {minimo} y {maximo}.")
    return numero


def evaluar(funcion: Funcion, *puntos: float) -> float:
    """Evalúa una función en un punto real e identifica fallos de dominio."""
    try:
        argumentos_validos = tuple(real(punto, "Argumento") for punto in puntos)
        return real(funcion(*argumentos_validos), "La evaluación")
    except (ArithmeticError, TypeError, ValueError):
        argumentos = ", ".join(str(p) for p in puntos)
        raise ValueError(f"La función no es real y finita en ({argumentos}).") from None


def suma_real(valores: Iterable[float], nombre: str) -> float:
    """Suma valores con compensación y detecta desbordamiento."""
    try:
        return real(fsum(valores), nombre)
    except (OverflowError, ValueError):
        raise ValueError(f"{nombre} supera el rango numérico.") from None


def nodos(datos: Iterable, minimo: int = 2, maximo: int = 10001,
          ordenar: bool = False) -> list[tuple[float, float]]:
    try:
        filas = iter(datos)
    except TypeError:
        raise ValueError("Ingrese una tabla con dos columnas.") from None
    puntos = []
    for i, fila in enumerate(filas, 1):
        if i > maximo:
            raise ValueError(f"Se admiten hasta {maximo} filas de dos columnas.")
        try:
            if isinstance(fila, (str, bytes)):
                raise TypeError
            izquierda, derecha = fila
        except (TypeError, ValueError):
            raise ValueError(f"La fila {i} debe contener dos columnas.") from None
        puntos.append((real(izquierda, f"x en fila {i}"), real(derecha, f"y en fila {i}")))
    if len(puntos) < minimo:
        raise ValueError(f"Se necesitan al menos {minimo} puntos.")
    if len({x for x, _ in puntos}) != len(puntos):
        raise ValueError("Las abscisas deben ser distintas.")
    return sorted(puntos) if ordenar else puntos


def paso_uniforme(puntos: list[tuple[float, float]]) -> float:
    h = positivo((puntos[-1][0] - puntos[0][0]) / (len(puntos) - 1),
                 "Espaciamiento")
    if any(not isclose(b[0] - a[0], h, rel_tol=1e-6)
           for a, b in zip(puntos, puntos[1:])):
        raise ValueError("Los nodos deben estar equiespaciados.")
    return h
