"""Referencia simbólica opcional con tiempo de cálculo acotado."""
from functools import lru_cache
from multiprocessing import get_context
from multiprocessing.connection import Connection

import sympy as sp


def _integrar(envio: Connection, expr: sp.Expr, x: sp.Symbol, a: float, b: float) -> None:
    """Calcula una referencia en un proceso que se puede detener."""
    try:
        exacta = sp.integrate(expr, (x, sp.Rational(str(a)), sp.Rational(str(b))))
        if not exacta.has(sp.Integral) and exacta.is_real is True and exacta.is_finite is True:
            envio.send((float(exacta), str(exacta)))
        else:
            envio.send((None, None))
    except Exception:
        envio.send((None, None))
    finally:
        envio.close()


@lru_cache(maxsize=32)
def referencia_integral(expr: sp.Expr, x: sp.Symbol, a: float, b: float) -> tuple:
    """Intenta obtener un valor exacto y reutiliza resultados por expresión e intervalo."""
    contexto = get_context("spawn")
    lectura, escritura = contexto.Pipe(duplex=False)
    proceso = contexto.Process(target=_integrar, args=(escritura, expr, x, a, b), daemon=True)
    with lectura, escritura:
        try:
            proceso.start()
        except (OSError, RuntimeError):
            return None, None
        escritura.close()
        try:
            return lectura.recv() if lectura.poll(4.0) else (None, None)
        except EOFError:
            return None, None
        finally:
            if proceso.is_alive():
                proceso.terminate()
            proceso.join(timeout=.5)
            if proceso.is_alive():
                proceso.kill()
                proceso.join()
            proceso.close()
