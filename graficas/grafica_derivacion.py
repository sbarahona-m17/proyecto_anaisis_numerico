"""Cinco nodos, tangente y sensibilidad al paso."""
from matplotlib.axes import Axes

from graficas.comun import Dibujo, curva, errores_positivos, escala_error, rotular
from utilidades.comparaciones import Calculo


def dibujos(calculo: Calculo, paso: int | None = None) -> dict[str, Dibujo]:
    r = next(iter(calculo.resultados.values()))
    if not r.convergio:
        return {}

    def nodos(ax: Axes) -> None:
        rotular(ax, "Nodos y recta tangente estimada", "x", "f(x)")
        xs, ys = zip(*r.extra["puntos"])
        visibles = len(xs) if paso is None else paso + 1
        centro = xs[2]
        if r.extra["función"] is not None:
            curva(ax, r.extra["función"], xs[0], xs[-1], "f(x)")
        ax.scatter(xs[:visibles], ys[:visibles], marker="o", label="Nodos usados")
        ax.scatter(centro, ys[2], marker="D", label="Punto central")
        ax.plot(xs, [ys[2] + r.valor * (x - centro) for x in xs],
                linestyle="--", label="Tangente aproximada")

    def error(ax: Axes) -> None:
        rotular(ax, "Truncamiento y redondeo al variar h", "Paso h", "Error absoluto")
        for i in (1, 2):
            errores_positivos(ax, [(fila[0], fila[i]) for fila in r.extra["curva"]],
                              f"Derivada de orden {i}")
        escala_error(ax, log_x=True)
        ax.invert_xaxis()

    return {"Nodos y tangente": nodos, "Error frente a h": error}
