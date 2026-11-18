"""Métodos cerrados y abiertos para ecuaciones escalares."""
from math import isclose, isfinite

from nucleo.resultado import Resultado
from utilidades.errores import errores
from utilidades.parser import Expresion
from utilidades.validaciones import Funcion, entero, evaluar, positivo, real


def _cociente_secante(fa: float, fb: float) -> float | None:
    """Devuelve fb / (fb - fa), incluso si la resta directa desborda."""
    if fa == fb:
        return None
    diferencia = fb - fa
    if not isfinite(diferencia):
        escala = max(abs(fa), abs(fb))
        fa, fb = fa / escala, fb / escala
        diferencia = fb - fa
    return fb / diferencia


def _resolver(metodo: str, f: Funcion, inicial: float, segundo: float | None,
              tol: float, max_iter: int, criterio: str,
              derivada: Funcion | None = None) -> Resultado:
    tol = positivo(tol, "Tolerancia")
    limite = entero(max_iter, "Máximo de iteraciones")
    if criterio not in ("Absoluto", "Relativo (%)", "Residuo"):
        raise ValueError("Seleccione un criterio de parada válido.")
    cerrado = metodo in ("Bisección", "Falsa posición")
    a = real(inicial, "Primer punto")
    b = a if segundo is None else real(segundo, "Segundo punto")
    if cerrado and b <= a:
        raise ValueError("El extremo inferior debe ser menor que el superior.")
    if metodo == "Secante" and a == b:
        raise ValueError("Las aproximaciones de secante deben ser distintas.")
    fa = evaluar(f, a)
    fb = fa if segundo is None else evaluar(f, b)
    escala_residuo = min(abs(fa), abs(fb))
    filas: list[dict] = []
    extra = {"función": f, "iniciales": (a, b), "método": metodo}
    if isinstance(derivada, Expresion):
        extra["Derivada simbólica"] = str(derivada.simbolica)

    def terminar(valor: float, residuo: float, exito: bool, razon: str) -> Resultado:
        extra["Residuo"] = abs(residuo)
        extra["Iteraciones"] = len(filas)
        if filas:
            extra["Cambio absoluto"] = filas[-1]["Ea"]
            extra["Cambio relativo (%)"] = filas[-1]["Error relativo (%)"]
        return Resultado(valor, exito, razon, filas, extra)

    for punto, valor in ((a, fa), (b, fb)):
        if valor == 0:
            return terminar(punto, valor, True, "Raíz exacta en un punto inicial.")
    if cerrado and (fa < 0) == (fb < 0):
        raise ValueError(f"El intervalo no presenta cambio de signo: f(a)={fa:g}, f(b)={fb:g}.")

    previo = None if cerrado else b
    f_previo = fb
    reciente = [b]
    c, fc = b, fb
    for n in range(1, limite + 1):
        try:
            if cerrado:
                if metodo == "Bisección":
                    amplitud = b - a
                    candidato = a + amplitud / 2 if isfinite(amplitud) else a / 2 + b / 2
                else:
                    # Escalar ambas ordenadas evita desbordar su diferencia.
                    escala = max(abs(fa), abs(fb))
                    peso = abs(fa / escala) / (abs(fa / escala) + abs(fb / escala))
                    candidato = (1 - peso) * a + peso * b
                fila = {"n": n, "a": a, "b": b, "c": candidato, "f(a)": fa, "f(b)": fb}
            elif derivada is not None:
                pendiente = evaluar(derivada, b)
                if pendiente == 0:
                    return terminar(c, fc, False, "Derivada nula.")
                candidato = b - fb / pendiente
                fila = {"n": n, "xₙ": b, "f(xₙ)": fb, "f′(xₙ)": pendiente,
                        "x siguiente": candidato}
            else:
                cociente = _cociente_secante(fa, fb)
                if cociente is None:
                    return terminar(c, fc, False, "Denominador nulo en secante.")
                distancia = b - a
                avance = (cociente * distancia if isfinite(distancia)
                          else cociente * b - cociente * a)
                candidato = b - avance
                fila = {"n": n, "x anterior": a, "xₙ": b, "f(x anterior)": fa,
                        "f(xₙ)": fb, "x siguiente": candidato}
            candidato = real(candidato, "Aproximación")
            fc_nuevo = evaluar(f, candidato)
        except ValueError as error:
            return terminar(c, fc, False, f"Iteración detenida. {error}")
        c, fc = candidato, fc_nuevo
        metrica = errores(c, previo)
        ea = metrica["Error absoluto"]
        relativo = errores(previo, c)["Error relativo (%)"] if previo is not None else None
        fila.update({"f(c)" if cerrado else "f(x siguiente)": fc,
                     "Ea": ea, "Error relativo (%)": relativo, "Residuo": abs(fc)})
        filas.append(fila)
        if fc == 0:
            return terminar(c, fc, True, "Raíz exacta en la evaluación.")
        medida = {"Absoluto": ea, "Relativo (%)": relativo, "Residuo": abs(fc)}[criterio]
        residuo_pequeno = abs(fc) <= min(tol, escala_residuo * 1e-14)
        if previo == c or (cerrado and c in (a, b)):
            if medida is not None and medida <= tol and (criterio == "Residuo" or residuo_pequeno):
                return terminar(c, fc, True, f"Criterio cumplido: {criterio}.")
            return terminar(c, fc, False, "Estancamiento sin confirmar una raíz.")
        if medida is not None and medida <= tol:
            if criterio == "Residuo" or residuo_pequeno or metodo == "Bisección":
                return terminar(c, fc, True, f"Criterio cumplido: {criterio}.")
            if metodo == "Newton-Raphson" and abs(fc) < abs(f_previo):
                return terminar(c, fc, True, f"Criterio cumplido: {criterio}.")
            if metodo in ("Falsa posición", "Secante"):
                # Un paso diminuto puede provenir de una pendiente calculada lejos
                # de la raíz. Estima la corrección con las últimas dos aproximaciones.
                cociente = _cociente_secante(f_previo, fc)
                if cociente is not None and abs(cociente) * medida <= tol:
                    return terminar(c, fc, True, f"Criterio cumplido: {criterio}.")
        if cerrado:
            if (fa < 0) != (fc < 0):
                b, fb = c, fc
            else:
                a, fa = c, fc
        else:
            if any(isclose(c, valor, rel_tol=1e-14, abs_tol=1e-15)
                   for valor in reciente[:-1]):
                return terminar(c, fc, False, "Se detectó un ciclo de aproximaciones.")
            reciente = (reciente + [c])[-8:]
            a, fa, b, fb = b, fb, c, fc
        previo, f_previo = c, fc
    return terminar(c, fc, False, "Se alcanzó el máximo de iteraciones.")


def biseccion(f: Funcion, a: float, b: float, tol: float = 1e-6,
              max_iter: int = 100, criterio: str = "Absoluto") -> Resultado:
    """Reduce a la mitad un intervalo con cambio de signo."""
    return _resolver("Bisección", f, a, b, tol, max_iter, criterio)


def falsa_posicion(f: Funcion, a: float, b: float, tol: float = 1e-6,
                   max_iter: int = 100, criterio: str = "Absoluto") -> Resultado:
    """Interpola linealmente dentro de un intervalo con cambio de signo."""
    return _resolver("Falsa posición", f, a, b, tol, max_iter, criterio)


def newton(f: Funcion, x0: float, tol: float = 1e-6, max_iter: int = 100,
           criterio: str = "Absoluto", derivada: Funcion | None = None) -> Resultado:
    """Actualiza la aproximación usando la tangente local."""
    if derivada is None:
        if not isinstance(f, Expresion):
            raise ValueError("Newton requiere una expresión o una derivada.")
        evaluar(f, real(x0, "Aproximación inicial"))
        derivada = f.derivada()
    return _resolver("Newton-Raphson", f, x0, None, tol, max_iter, criterio, derivada)


def secante(f: Funcion, x0: float, x1: float, tol: float = 1e-6,
            max_iter: int = 100, criterio: str = "Absoluto") -> Resultado:
    """Usa dos iteraciones sucesivas para estimar la pendiente."""
    return _resolver("Secante", f, x0, x1, tol, max_iter, criterio)
