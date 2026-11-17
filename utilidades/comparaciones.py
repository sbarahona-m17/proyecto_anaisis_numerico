"""Orquestación sin GUI de métodos, reportes y comparaciones."""
from dataclasses import dataclass, field
from math import isclose, log2

import sympy as sp

from nucleo import derivacion, edo, integracion, interpolacion, raices
from nucleo.resultado import Resultado
from utilidades.errores import errores
from utilidades.ejemplos import DERIVACION, INTERPOLACION, RAICES
from utilidades.parser import interpretar
from utilidades.validaciones import evaluar, real

METODOS = dict(zip(("Raíces", "Diferenciación", "Interpolación", "Integración", "EDO"),
                   (RAICES, DERIVACION, INTERPOLACION, integracion.METODOS, edo.METODOS)))


@dataclass
class Calculo:
    """Agrupa métodos calculados, resumen y series de comparación."""
    modulo: str
    resultados: dict[str, Resultado]
    comparacion: bool
    resumen: list[dict] = field(default_factory=list)
    detalles: str = ""
    refinamiento: dict[str, list[tuple[float, float]]] = field(default_factory=dict)


def calcular(modulo: str, metodo: str, campos: dict, datos: list,
             comparar: bool = False) -> Calculo:
    """Prepara el problema, ejecuta los métodos y resume el resultado."""
    if metodo not in METODOS[modulo]:
        raise ValueError("Seleccione un método.")
    c = campos
    tabular = c.get("modo") == "Tabla" or modulo == "Interpolación"
    f = None if tabular else interpretar(c["f"], ("t", "y") if modulo == "EDO" else ("x",))
    exacta = (interpretar(c["exacta"], ("t",))
              if modulo == "EDO" and c.get("exacta", "").strip() else None)

    raiz_exacta = (real(c["referencia"], "Raíz exacta")
                   if modulo == "Raíces" and str(c.get("referencia", "")).strip() else None)

    if raiz_exacta is not None and abs(evaluar(f, raiz_exacta)) > 1e-8:
        raise ValueError("La raíz de referencia no satisface f(x)=0 dentro de 10⁻⁸.")

    def ejecutar(nombre: str) -> Resultado:
        if modulo == "Raíces":
            funciones = (raices.biseccion, raices.falsa_posicion, raices.newton, raices.secante)
            argumentos = (("a", "b"), ("a", "b"), ("x0",), ("s0", "s1"))
            indice = RAICES.index(nombre)
            r = funciones[indice](f, *(c[k] for k in argumentos[indice]),
                                   tol=c["tol"], max_iter=c["max_iter"], criterio=c["criterio"])
            if raiz_exacta is not None:
                r.extra.update({"Referencia": raiz_exacta, **errores(r.valor, raiz_exacta)})
            return r
        if modulo == "Diferenciación":
            return derivacion.cinco_puntos(f, c["x0"], c["h"], datos if tabular else None)
        if modulo == "Interpolación":
            funcion = interpolacion.lagrange if nombre == "Lagrange" else interpolacion.newton
            consultas = str(c["consultas"]).replace(",", " ").split()
            return funcion(datos, consultas)
        if modulo == "Integración":
            return integracion.integrar(nombre, f, c["a"], c["b"], c["n"],
                                        datos if tabular else None,
                                        c["unidad"] == "Minutos y Mbps")
        usar_h = c["paso"] == "Tamaño de paso h"
        return edo.resolver(nombre, f, c["t0"], c["y0"], c["tf"],
                            h=c["h"] if usar_h else None, n=None if usar_h else c["n"],
                            exacta=exacta)

    conjunto = Calculo(modulo, {}, comparar)
    for nombre in METODOS[modulo] if comparar else (metodo,):
        try:
            resultado = ejecutar(nombre)
        except (ArithmeticError, ValueError) as error:
            if not comparar:
                raise
            resultado = Resultado(None, False, str(error))
        conjunto.resultados[nombre] = resultado
    for nombre, r in conjunto.resultados.items():
        filas = r.extra.get("resumen")
        if filas:
            conjunto.resumen.extend({"Método": nombre, **fila} for fila in filas)
        else:
            ultimo = r.tabla[-1] if r.tabla else {}
            conjunto.resumen.append({
                "Método": nombre, "Resultado": r.valor,
                "Estado": "Completado" if r.convergio else "Detenido",
                "Mensaje": r.mensaje, "Filas": len(r.tabla),
                **{k: v for k, v in r.extra.items() if k in (
                    "Iteraciones", "Pasos", "Subintervalos", "Residuo", "Referencia",
                    "Error absoluto", "Error relativo (%)", "Volumen (GB)")},
                **{k: ultimo[k] for k in ("Ea", "Error relativo (%)")
                   if modulo == "Raíces" and k in ultimo},
            })

    if modulo == "Interpolación" and comparar and all(r.convergio for r in conjunto.resultados.values()):
        lag, new = conjunto.resultados.values()
        equivalente = sp.expand(lag.extra["expandido"] - new.extra["expandido"]) == 0
        pares = zip(lag.extra["resumen"], new.extra["resumen"])
        for a, b in pares:
            diferencia = abs(a["Resultado"] - b["Resultado"])
            conjunto.resumen.append({"Método": "Diferencia entre métodos", "x*": a["x*"],
                                     "Resultado": diferencia})
            equivalente &= isclose(a["Resultado"], b["Resultado"], rel_tol=1e-9, abs_tol=1e-9)
        conjunto.detalles = ("Equivalencia simbólica y numérica verificada." if equivalente
                             else "Los métodos discrepan. Revise el condicionamiento y la implementación.")
    if modulo == "Integración" and f is not None:
        referencia = next((r.extra["Referencia"] for r in conjunto.resultados.values()
                           if r.extra.get("Referencia") is not None), None)
        if comparar:
            base = conjunto.resumen[0]["Resultado"]
            for fila in conjunto.resumen:
                if base is not None and fila["Resultado"] is not None:
                    fila["Diferencia vs. trapecio simple"] = fila["Resultado"] - base
        if referencia is not None:
            for regla in (integracion.METODOS[1], integracion.METODOS[3]):
                curva = []
                for n in (2, 4, 8, 16, 32, 64, 128):
                    try:
                        aprox = integracion.integrar(regla, f, c["a"], c["b"], n,
                                                      referencia=False,
                                                      transferencia=c["unidad"] == "Minutos y Mbps").valor
                        curva.append((n, abs(aprox - referencia)))
                    except (ArithmeticError, ValueError):
                        continue
                conjunto.refinamiento[regla] = curva
        conjunto.detalles = ("Para funciones suaves, el error global es O(h²) en trapecio "
                             "y O(h⁴) en Simpson. La pendiente observada depende del integrando.")
    if modulo == "EDO" and comparar:
        conjunto.detalles = ("Órdenes globales teóricos: Euler 1, Heun 2, Runge-Kutta 4. "
                             "Sin solución exacta se muestra el cambio respecto a la malla refinada.")
        for fila, (nombre, r) in zip(conjunto.resumen, conjunto.resultados.items()):
            if not r.convergio:
                continue
            try:
                h = r.extra["h"]
                fino = edo.resolver(nombre, f, c["t0"], c["y0"], c["tf"],
                                    h=h / 2, exacta=exacta)
                if not fino.convergio:
                    raise ValueError(fino.mensaje)
                previo, nuevo = r.extra.get("Error absoluto"), fino.extra.get("Error absoluto")
                fila.update({"h": h, "h/2": h / 2, "y final con h/2": fino.valor,
                             "Pasos con h/2": fino.extra["Pasos"],
                             "Cambio de malla": abs(r.valor - fino.valor),
                             "Error con h/2": nuevo,
                             "Orden observado": log2(previo / nuevo) if previo and nuevo else None})
            except (ArithmeticError, ValueError) as error:
                fila["Refinamiento"] = str(error)
    if modulo == "Diferenciación":
        conjunto.detalles = ("Cada fórmula estima una magnitud distinta. En una función suave, "
                             "el truncamiento disminuye como h⁴. Con pasos muy pequeños, la "
                             "cancelación y la división por h o h² amplifican el redondeo.")
    return conjunto
