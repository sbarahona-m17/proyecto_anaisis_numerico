"""Ilustración matemática de la pantalla de inicio."""
from math import sin
import tkinter as tk

from interfaz.estilos import MARINO, MENTA


class Trazo(tk.Canvas):
    """Ilustra una curva suave y sus muestras sin cargar archivos externos."""

    def __init__(self, master: tk.Misc):
        super().__init__(master, width=320, height=184, background=MARINO,
                         borderwidth=0, highlightthickness=0)
        self.bind("<Configure>", self._dibujar)

    def _dibujar(self, evento: tk.Event) -> None:
        self.delete("all")
        ancho, alto = evento.width, evento.height
        margen = 15
        if ancho < 70 or alto < 35:
            return
        for x in range(margen, ancho - margen, 28):
            self.create_line(x, margen, x, alto - margen, fill="#223753")
        for y in range(margen, alto - margen, 24):
            self.create_line(margen, y, ancho - margen, y, fill="#223753")
        eje = alto * .57
        self.create_line(margen, eje, ancho - margen, eje, fill="#486285")

        def punto(u: float) -> tuple[float, float]:
            return (margen + u * (ancho - 2 * margen),
                    eje - .31 * alto * sin(7.5 * u - 1.15) - .09 * alto * u)

        curva = [coord for i in range(81) for coord in punto(i / 80)]
        self.create_line(*curva, fill="#1f675f", width=8)
        self.create_line(*curva, fill=MENTA, width=2)
        for u in (.10, .25, .40, .55, .70, .85):
            x, y = punto(u)
            self.create_line(x, eje, x, y, fill="#537697", dash=(3, 4))
            self.create_oval(x - 4, y - 4, x + 4, y + 4, fill=MARINO,
                             outline="#b1ffe9", width=2)
