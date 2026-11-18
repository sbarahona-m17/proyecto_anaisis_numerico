"""Áreas y refinamiento para las reglas de cuadratura."""
import numpy as np
from matplotlib.axes import Axes

from graficas.comun import Dibujo, curva, errores_positivos, escala_error, rotular
from utilidades.comparaciones import Calculo


def dibujos(calculo: Calculo, paso: int | None = None) -> dict[str, Dibujo]:
    resultados = {k: r for k, r in calculo.resultados.items() if r.convergio}
    if not resultados:
        return {}
    primero = next(iter(resultados.values()))
    colores = ["#087fbb", "#008b79", "#b45287", "#c87b00"]

    def area(ax: Axes, seleccion: dict) -> None:
        transferencia = primero.extra.get("Unidad") == "Mb"
        rotular(ax, "Área y aproximaciones de Newton–Cotes",
                "Tiempo (min)" if transferencia else "x", "Tasa (Mbps)" if transferencia else "f(x)")
        a, b = primero.extra["puntos"][0][0], primero.extra["puntos"][-1][0]
        f = primero.extra["función"]
        if f:
            curva(ax, f, a, b, "f(x)", color="#8092a7")
        ax.axhline(0, color="#8092a7", linewidth=.8)
        for (nombre, r), color in zip(seleccion.items(), colores):
            puntos = r.extra["puntos"]
            grado = 2 if nombre.startswith("Simpson") else 1
            cuantos = len(puntos) - 1 if paso is None else min(paso, len(puntos) - 1)
            bloques = range(0, cuantos - grado + 1, grado)
            xs_trazo, ys_trazo = [], []
            bordes_x, bordes_y = [], []
            salto = max(1, len(bloques) // 250)
            for i in bloques[::salto]:
                xs, ys = zip(*puntos[i:i + grado + 1])
                abscisas = np.linspace(xs[0], xs[-1], 12 if grado == 2 else 2)
                u = (abscisas - xs[0]) / (xs[-1] - xs[0])
                if grado == 2:
                    v = (xs[1] - xs[0]) / (xs[-1] - xs[0])
                    ordenadas = (ys[0] * (u-v) * (u-1) / v
                                 + ys[1] * u * (u-1) / (v * (v-1))
                                 + ys[2] * u * (u-v) / (1-v))
                else:
                    ordenadas = (1-u) * ys[0] + u * ys[1]
                xs_trazo.extend([*abscisas, np.nan])
                ys_trazo.extend([*ordenadas, np.nan])
                bordes_x.extend((xs[0], xs[-1]))
                bordes_y.extend((ys[0], ys[-1]))
            ax.plot(xs_trazo, ys_trazo, color=color, label=nombre)
            ax.fill_between(xs_trazo, ys_trazo, color=color, alpha=.14)
            if bordes_x:
                ax.vlines(bordes_x, 0, bordes_y, color=color, linewidth=.6, alpha=.45)
            xs, ys = zip(*puntos[:cuantos + 1:salto])
            ax.scatter(xs, ys, s=12, color=color)

    def error(ax: Axes) -> None:
        rotular(ax, "Error frente al número de subintervalos", "Subintervalos n", "Error absoluto")
        for nombre, pares in calculo.refinamiento.items():
            errores_positivos(ax, pares, nombre)
        escala_error(ax, log_x=True)

    vistas = {"Área conjunta" if calculo.comparacion else "Área": lambda ax: area(ax, resultados)}
    if calculo.comparacion:
        vistas.update({
            m.replace("Trapecio ", "T. ").replace("Simpson 1/3 ", "S. "):
            (lambda ax, m=m, r=r: area(ax, {m: r}))
            for m, r in resultados.items()
        })
    vistas["Error frente a n"] = error
    return vistas
