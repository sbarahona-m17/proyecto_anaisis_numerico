"""Soluciones, campo de pendientes y errores de EDO."""
import numpy as np
from matplotlib.axes import Axes

from graficas.comun import Dibujo, curva, errores_positivos, escala_error, rotular
from utilidades.comparaciones import Calculo
from utilidades.validaciones import evaluar


def dibujos(calculo: Calculo, paso: int | None = None) -> dict[str, Dibujo]:
    resultados = {k: r for k, r in calculo.resultados.items() if r.tabla}
    if not resultados:
        return {}
    primero = next(iter(resultados.values()))

    def filas(r):
        return r.tabla if paso is None else r.tabla[:paso + 1]

    def soluciones(ax: Axes, campo: bool = False) -> None:
        rotular(ax, "Campo de pendientes y soluciones" if campo else "Soluciones de la EDO", "t", "y(t)")
        a, b = primero.extra["Intervalo"]
        if campo:
            ordenadas = [f["y"] for r in resultados.values() for f in filas(r)]
            ymin, ymax = min(ordenadas), max(ordenadas)
            delta = max((ymax - ymin) * .1, .2)
            t, y = np.meshgrid(np.linspace(a, b, 19), np.linspace(ymin-delta, ymax+delta, 14))
            v = np.full(t.shape, np.nan)
            for i in np.ndindex(t.shape):
                try:
                    v[i] = evaluar(primero.extra["función"], t[i], y[i])
                except ValueError:
                    continue
            norma = np.hypot(1, v)
            ax.quiver(t, y, 1/norma, v/norma, color="#8092a7", alpha=.5,
                      angles="xy", scale=33, pivot="mid")
        if primero.extra["exacta"]:
            curva(ax, primero.extra["exacta"], a, b, "Referencia exacta", linestyle="--")
        for nombre, r in resultados.items():
            vista = filas(r)
            ax.plot([f["t"] for f in vista], [f["y"] for f in vista],
                    marker="o", markersize=3, markevery=max(1, len(vista)//100), label=nombre)

    def error(ax: Axes) -> None:
        rotular(ax, "Error absoluto de la solución", "t", "Error absoluto")
        for nombre, r in resultados.items():
            errores_positivos(ax, [(f["t"], f["Error absoluto"]) for f in filas(r)], nombre)
        escala_error(ax)

    return {"Soluciones": soluciones, "Campo de pendientes": lambda ax: soluciones(ax, True),
            "Error frente a t": error}
