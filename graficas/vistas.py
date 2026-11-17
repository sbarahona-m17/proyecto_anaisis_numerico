"""Selección y acabado común de figuras."""
from matplotlib.figure import Figure

from graficas import (grafica_derivacion, grafica_edo, grafica_integracion,
                      grafica_interpolacion, grafica_raices)
from graficas.comun import Dibujo
from utilidades.comparaciones import Calculo

MODULOS = dict(zip(("Raíces", "Diferenciación", "Interpolación", "Integración", "EDO"),
                   (grafica_raices, grafica_derivacion, grafica_interpolacion,
                    grafica_integracion, grafica_edo)))


def vistas(calculo: Calculo, paso: int | None = None) -> dict[str, Dibujo]:
    """Recupera las pestañas correspondientes al cálculo."""
    return MODULOS[calculo.modulo].dibujos(calculo, paso)


def dibujar(figura: Figure, dibujo: Dibujo, oscuro: bool = False) -> None:
    """Actualiza la figura respetando el tema seleccionado."""
    figura.clear()
    fondo, papel, tinta, detalle = (
        ("#101827", "#172439", "#edf4ff", "#405471") if oscuro
        else ("#f6f8fc", "#ffffff", "#172640", "#a5b6cc")
    )
    figura.set_facecolor(fondo)
    ax = figura.add_subplot()
    ax.set_facecolor(papel)
    colores = (["#66ddc2", "#80aaff", "#fab276", "#c5a7ff", "#f38ea9"] if oscuro
               else ["#087f72", "#356abd", "#a65a18", "#7952b6", "#ac4365"])
    ax.set_prop_cycle(color=colores)
    dibujo(ax)
    ax.set_title(ax.get_title(), color=tinta, fontweight="bold", pad=10)
    ax.set_axisbelow(True)
    ax.grid(color=detalle, alpha=.22, which="both")
    ax.xaxis.label.set_color(tinta)
    ax.yaxis.label.set_color(tinta)
    ax.tick_params(colors=tinta, labelsize=8)
    for lado, linea in ax.spines.items():
        linea.set_visible(lado in ("left", "bottom"))
        linea.set_color(detalle)
    elementos, nombres = ax.get_legend_handles_labels()
    if elementos:
        ax.legend(elementos, nombres, loc="best", ncols=2 if len(elementos) > 5 else 1,
                  fontsize=8, labelcolor=tinta, facecolor=papel, edgecolor=detalle)
    for texto in ax.texts:
        texto.set_color(tinta)
