"""Métodos explícitos de un paso para una EDO escalar."""
from math import ceil, isclose

from nucleo.resultado import Resultado
from utilidades.errores import errores
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

    def datos_paso(i: int, t: float, y: float) -> dict:
        referencia = evaluar(exacta, t) if exacta else None
        return {"i": i, "t": t, "y": y, "Referencia": referencia, **errores(y, referencia)}

    filas = [datos_paso(0, t0, y0)]
    if exacta and not isclose(filas[0]["Referencia"], y0, rel_tol=1e-7, abs_tol=1e-9):
        raise ValueError("La referencia exacta no satisface la condición inicial.")
    extra = {"función": f, "exacta": exacta, "h": paso, "Intervalo": (t0, tf)}
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
                incremento = dt * (k1 + k2) / 2
            else:
                k2 = evaluar(f, t + dt / 2, y + dt * k1 / 2)
                k3 = evaluar(f, t + dt / 2, y + dt * k2 / 2)
                k4 = evaluar(f, siguiente, y + dt * k3)
                etapas.update({"k2": k2, "k3": k3, "k4": k4})
                incremento = dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            nuevo = real(y + incremento, "Solución")
            fila = datos_paso(i, siguiente, nuevo)
        except ValueError as error:
            return Resultado(y, False, f"Paso {i} detenido. {error}", filas, extra)
        if metodo == "Heun":
            etapas["Corrector"] = nuevo
        filas.append({**fila, **etapas})
        t, y = siguiente, nuevo
    mensaje = "Se alcanzó el tiempo final."
    if ajustado:
        mensaje += f" Último paso acortado a {filas[-1]['Paso']:.12g}."
    extra.update({"Pasos": cantidad, "Referencia": filas[-1]["Referencia"],
                  **errores(y, filas[-1]["Referencia"])})
    return Resultado(y, True, mensaje, filas, extra)
