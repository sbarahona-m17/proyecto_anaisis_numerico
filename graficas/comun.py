"""Primitivas de dibujo compartidas."""
from collections.abc import Callable

import numpy as np
from matplotlib.axes import Axes

from utilidades.validaciones import Funcion, evaluar

Dibujo = Callable[[Axes], None]


def curva(ax: Axes, funcion: Funcion, a: float, b: float, etiqueta: str,
          **opciones) -> None:
    """Dibuja una curva con huecos donde la función queda fuera del dominio."""
    xs = np.linspace(a, b, 260)
    ys = []
    for x in xs:
        try:
            ys.append(evaluar(funcion, x))
        except ValueError:
            ys.append(np.nan)
    ax.plot(xs, ys, label=etiqueta, **opciones)


def rotular(ax: Axes, titulo: str, x: str, y: str) -> None:
    """Aplica el rotulado y la cuadrícula comunes."""
    ax.set(title=titulo, xlabel=x, ylabel=y)
    ax.grid(alpha=.23, which="both")


def sin_datos(ax: Axes, texto: str) -> None:
    """Explica la ausencia de una serie graficable."""
    ax.text(.5, .5, texto, transform=ax.transAxes, ha="center", va="center",
            wrap=True)


def escala_error(ax: Axes, log_x: bool = False) -> None:
    """Configura escala logarítmica y evita dibujar ceros artificiales."""
    ax.set_yscale("log")
    if log_x:
        ax.set_xscale("log")
    if not ax.has_data():
        sin_datos(ax, "Sin errores positivos con referencia disponible.")


def errores_positivos(ax: Axes, pares: list, nombre: str) -> None:
    """Conserva los huecos y omite ceros en escala logarítmica."""
    if any(y is not None and y > 0 for _, y in pares):
        ax.plot([x for x, _ in pares],
                [y if y is not None and y > 0 else np.nan for _, y in pares],
                marker="o", markersize=3, label=nombre)
