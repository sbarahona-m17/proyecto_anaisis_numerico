"""Métodos explícitos de un paso para una EDO escalar."""
from math import ceil, fsum, isclose

from nucleo.resultado import Resultado
from utilidades.errores import errores
from utilidades.parser import Expresion
from utilidades.validaciones import Funcion, entero, evaluar, positivo, real

METODOS = ("Euler", "Heun", "Runge-Kutta 4")


def resolver(metodo: str, f: Funcion, t0: float, y0: float, tf: float,
             h: float | None = None, n: int | None = None,
             exacta: Funcion | None = None) -> Resultado:
    """Resuelve la EDO acortando el último paso, si es necesario."""
    if metodo not in METODOS:
        raise ValueError("Seleccione un método de EDO válido.")
    t0, y0, tf = real(t0, "Tiempo inicial"), real(y0, "Valor inicial"), real(tf, "Tiempo final")
    amplitud = positivo(tf - t0, "Diferencia tf − t₀")
    if (h is None) == (n is None):
        raise ValueError("Indique exactamente uno: paso h o número de pasos N.")
    ajustado = False
    if n is not None:
        cantidad = entero(n, "Número de pasos")
        paso = amplitud / cantidad
    else:
        paso = positivo(h, "Paso h")
        cociente = real(amplitud / paso, "Número de pasos")
        entero_cercano = round(cociente)
        uniforme = entero_cercano >= 1 and isclose(cociente, entero_cercano, rel_tol=1e-14)
        cantidad = entero(entero_cercano if uniforme else ceil(cociente), "Número de pasos")
        ajustado = not uniforme
    if t0 + paso == t0:
        raise ValueError("El paso es demasiado pequeño para avanzar en el tiempo.")
    k1_inicial = evaluar(f, t0, y0)

    if exacta is not None:
        y_referencia = evaluar(exacta, t0)
        if not isclose(y_referencia, y0, rel_tol=1e-7, abs_tol=1e-9):
            raise ValueError("La referencia exacta no satisface la condición inicial.")
    if isinstance(exacta, Expresion):
        derivada = exacta.derivada()
        for t in (t0, t0 + amplitud / 2, tf):
            pendiente = evaluar(derivada, t)
            esperada = evaluar(f, t, evaluar(exacta, t))
            if not isclose(pendiente, esperada, rel_tol=1e-7, abs_tol=1e-9):
                raise ValueError(f"La referencia exacta no satisface la EDO en t={t:g}.")

    def datos_paso(i: int, t: float, y: float) -> dict:
        referencia = evaluar(exacta, t) if exacta else None
        return {"i": i, "t": t, "y": y, "Referencia": referencia, **errores(y, referencia)}

    filas = [datos_paso(0, t0, y0)]
    extra = {"función": f, "exacta": exacta, "h": paso, "Intervalo": (t0, tf)}

    def terminar(convergio: bool, mensaje: str) -> Resultado:
        ultimo = filas[-1]
        extra.update({"Pasos": len(filas) - 1, "Tiempo alcanzado": ultimo["t"],
                      "Referencia": ultimo["Referencia"], **errores(ultimo["y"], ultimo["Referencia"])})
        return Resultado(ultimo["y"], convergio, mensaje, filas, extra)

    t, y = t0, y0
    for i in range(1, cantidad + 1):
        siguiente = tf if i == cantidad else t0 + i * paso
        dt = siguiente - t
        etapas = {"Paso": dt}
        try:
            if dt <= 0:
                raise ValueError("El paso no puede representarse en este intervalo.")
            k1 = k1_inicial if i == 1 else evaluar(f, t, y)
            etapas["k1"] = k1
            if metodo == "Euler":
                incremento = dt * k1
            elif metodo == "Heun":
                predictor = y + dt * k1
                k2 = evaluar(f, siguiente, predictor)
                etapas.update({"Predictor": predictor, "k2": k2})
                incremento = dt * (k1 / 2 + k2 / 2)
            else:
                medio = dt / 2
                k2 = evaluar(f, t + medio, y + medio * k1)
                k3 = evaluar(f, t + medio, y + medio * k2)
                k4 = evaluar(f, siguiente, y + dt * k3)
                etapas.update({"k2": k2, "k3": k3, "k4": k4})
                incremento = dt * fsum((k1 / 6, k2 / 3, k3 / 3, k4 / 6))
            nuevo = real(y + incremento, "Solución")
            fila = datos_paso(i, siguiente, nuevo)
        except (ArithmeticError, ValueError) as error:
            return terminar(False, f"Paso {i} detenido en t={siguiente:g}. {error}")
        if metodo == "Heun":
            etapas["Corrector"] = nuevo
        filas.append({**fila, **etapas})
        t, y = siguiente, nuevo
    mensaje = "Se alcanzó el tiempo final."
    if ajustado:
        mensaje += f" Último paso acortado a {filas[-1]['Paso']:.12g}."
    return terminar(True, mensaje)
