"""Función, construcciones geométricas y convergencia de raíces."""
from matplotlib.axes import Axes

from graficas.comun import Dibujo, curva, errores_positivos, escala_error, rotular
from utilidades.comparaciones import Calculo


def dibujos(calculo: Calculo, paso: int | None = None) -> dict[str, Dibujo]:
    """Crea las vistas del método o la comparación."""
    resultados = [(m, r) for m, r in calculo.resultados.items() if "función" in r.extra]

    def filas(r):
        return r.tabla if paso is None else r.tabla[:paso + 1]

    def funcion(ax: Axes, geometria: bool = False) -> None:
        rotular(ax, "Geometría de las iteraciones" if geometria else "Raíces de f(x)", "x", "f(x)")
        ax.axhline(0, color="#8497aa", linewidth=.9, label="Eje horizontal")
        if not resultados:
            return
        iniciales = [p for _, r in resultados for p in r.extra["iniciales"]]
        if not geometria:
            iniciales.extend(r.valor for _, r in resultados if r.valor is not None)
        a, b = min(iniciales), max(iniciales)
        margen = max((b - a) * .12, abs(a) * .05, .4)
        curva(ax, resultados[0][1].extra["función"], a - margen, b + margen, "f(x)")
        for nombre, r in resultados:
            historial = filas(r)
            xs = [f.get("c", f.get("x siguiente")) for f in historial]
            ys = [f.get("f(c)", f.get("f(x siguiente)")) for f in historial]
            if not geometria:
                if xs:
                    ax.scatter(xs, ys, s=18, label=f"Aproximaciones · {nombre}")
                if paso is None and r.convergio:
                    ax.scatter(r.valor, 0, s=100, marker="*", label=f"Raíz · {nombre}")
                continue
            seleccion = historial[:7] if paso is None else historial[-1:]
            for i, fila in enumerate(seleccion):
                etiqueta = nombre if i == 0 else "_nolegend_"
                opacidad = .3 + .6 * (i + 1) / len(seleccion)
                if "a" in fila and nombre == "Bisección":
                    ax.hlines(0, fila["a"], fila["b"], color="#00a896", linewidth=3,
                              alpha=opacidad, label=etiqueta)
                    ax.vlines(fila["c"], 0, fila["f(c)"], alpha=opacidad)
                elif "a" in fila:
                    ax.plot([fila["a"], fila["b"]], [fila["f(a)"], fila["f(b)"]],
                            alpha=opacidad, label=etiqueta)
                elif "f′(xₙ)" in fila:
                    ax.plot([fila["xₙ"], fila["x siguiente"]], [fila["f(xₙ)"], 0],
                            alpha=opacidad, label=etiqueta)
                else:
                    x, y = fila["x siguiente"], 0
                    ax.plot([fila["x anterior"], fila["xₙ"], x],
                            [fila["f(x anterior)"], fila["f(xₙ)"], y],
                            alpha=opacidad, label=etiqueta)

    def error(ax: Axes) -> None:
        rotular(ax, "Convergencia de las aproximaciones", "Iteración", "Cambio absoluto")
        for nombre, r in resultados:
            errores_positivos(ax, [(f["n"], f["Ea"]) for f in filas(r)], nombre)
        escala_error(ax)

    return {"Función": funcion, "Geometría": lambda ax: funcion(ax, True), "Convergencia": error}
