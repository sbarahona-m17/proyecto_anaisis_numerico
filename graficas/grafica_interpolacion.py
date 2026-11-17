"""Interpolantes, bases de Lagrange y sumas parciales de Newton."""
from matplotlib.axes import Axes

from graficas.comun import Dibujo, curva, rotular
from utilidades.comparaciones import Calculo
from utilidades.parser import compilar
from nucleo.interpolacion import X


def dibujos(calculo: Calculo, paso: int | None = None) -> dict[str, Dibujo]:
    resultados = {k: r for k, r in calculo.resultados.items() if r.convergio}
    if not resultados:
        return {}
    primero = next(iter(resultados.values()))
    xs, ys = zip(*primero.extra["puntos"])

    def interpolante(ax: Axes) -> None:
        rotular(ax, "Interpolación a partir de datos", "x", "P(x)")
        ax.scatter(xs, ys, s=35, label="Nodos originales", zorder=4)
        consultas = [f["x*"] for f in primero.extra["resumen"]]
        a, b = min(*xs, *consultas), max(*xs, *consultas)
        for i, (nombre, r) in enumerate(resultados.items()):
            curva(ax, r.extra["función"], a, b, nombre,
                  linestyle="-" if i == 0 else "--")
        ax.scatter(consultas, [f["Resultado"] for f in primero.extra["resumen"]],
                   marker="D", label="Evaluaciones", zorder=5)

    def componentes(ax: Axes, nombre: str) -> None:
        lagrange = nombre == "Lagrange"
        rotular(ax, "Bases cardinales" if lagrange else "Polinomios parciales", "x", "Valor")
        lista = resultados[nombre].extra["componentes"]
        seleccion = list(enumerate(lista if paso is None else lista[:paso + 1]))
        for i, expr in seleccion:
            f = compilar(expr, (X,))
            curva(ax, f, min(xs), max(xs), f"{'L' if lagrange else 'P'}{i}")
        if lagrange:
            ax.scatter(xs, [0] * len(xs), marker="|", label="Abscisas de los nodos")

    vistas = {"Interpolante": interpolante}
    for nombre in resultados:
        vistas["Bases de Lagrange" if nombre == "Lagrange" else "Parciales de Newton"] = (
            lambda ax, m=nombre: componentes(ax, m))
    return vistas
