"""Ilustración matemática de la pantalla de inicio."""
from math import pi, sin
import tkinter as tk

from interfaz.estilos import MARINO, MENTA


class Trazo(tk.Canvas):
    """Muestra una función y sus nodos de muestreo en la portada."""

    def __init__(self, master: tk.Misc):
        super().__init__(master, width=310, height=181, background=MARINO,
                         borderwidth=0, highlightthickness=0)
        self.bind("<Configure>", self._dibujar)

    def _dibujar(self, evento: tk.Event) -> None:
        self.delete("all")
        ancho, alto = evento.width, evento.height
        if ancho < 170 or alto < 100:
            return
        izquierda, derecha = 34, ancho - 18
        arriba, abajo = 36, alto - 27
        eje = (arriba + abajo) / 2
        escala = (abajo - arriba) / 2
        self.create_rectangle(1, 1, ancho - 1, alto - 1, fill="#182b45", outline="#354b6a")

        def punto(u: float) -> tuple[float, float]:
            return izquierda + u * (derecha - izquierda), eje - escala * sin(2 * pi * u)

        for y, etiqueta in ((arriba, "1"), (eje, "0"), (abajo, "−1")):
            self.create_line(izquierda, y, derecha, y, fill="#486180" if y == eje else "#2c425f")
            self.create_text(izquierda - 9, y, text=etiqueta, anchor="e",
                             fill="#bacce3", font=("Segoe UI", 8))
        for i, etiqueta in enumerate(("0", "π/2", "π", "3π/2", "2π")):
            x, _ = punto(i / 4)
            self.create_line(x, arriba, x, abajo, fill="#2c425f")
            self.create_text(x, abajo + 13, text=etiqueta, fill="#bacce3", font=("Segoe UI", 8))
        self.create_text(izquierda, 17, text="f(x) = sen(x)", anchor="w",
                         fill="#e4efff", font=("Segoe UI Semibold", 9))
        self.create_oval(derecha - 54, 14, derecha - 48, 20, fill=MENTA, outline="")
        self.create_text(derecha - 42, 17, text="Nodos", anchor="w", fill="#bacce3",
                         font=("Segoe UI", 8))
        curva = [coord for i in range(121) for coord in punto(i / 120)]
        self.create_line(*curva, fill=MENTA, width=2)
        for u in (.125, .25, .375, .5, .625, .75, .875):
            x, y = punto(u)
            self.create_line(x, eje, x, y, fill="#64819f", dash=(2, 4))
            self.create_oval(x - 3, y - 3, x + 3, y + 3, fill=MENTA,
                             outline="#182b45", width=1)
