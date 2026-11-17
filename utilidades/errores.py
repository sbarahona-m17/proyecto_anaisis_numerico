"""Métricas de error de NumLab."""
from math import isfinite


def errores(valor: float, referencia: float | None) -> dict:
    """Calcula errores frente a una referencia, si existe."""
    absoluto = abs(valor - referencia) if referencia is not None else None
    relativo = (absoluto / abs(referencia) * 100
                if absoluto is not None and referencia else None)
    return {"Error absoluto": absoluto if absoluto is not None and isfinite(absoluto) else None,
            "Error relativo (%)": relativo if relativo is not None and isfinite(relativo) else None}
