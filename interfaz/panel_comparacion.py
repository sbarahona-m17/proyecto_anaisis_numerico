"""Texto de presentación y decisión de comparaciones."""
from utilidades.comparaciones import Calculo
from utilidades.formato import mostrar


def encabezado(calculo: Calculo, decimales: int) -> str:
    """Resume visualmente los resultados disponibles."""
    if calculo.comparacion:
        total = len(calculo.resultados)
        completos = sum(r.convergio for r in calculo.resultados.values())
        return f"Comparación · {completos} de {total} métodos completados"
    metodo, r = next(iter(calculo.resultados.items()))
    if calculo.modulo == "Diferenciación" and r.convergio:
        a, b = (mostrar(f["Resultado"], decimales) for f in r.extra["resumen"])
        if metodo == "Segunda derivada":
            return f"Segunda derivada  {b}     ·     Primera derivada  {a}"
        return f"Primera derivada  {a}     ·     Segunda derivada  {b}"
    nombre = metodo if r.convergio else f"{metodo} · última aproximación"
    return f"{nombre}   {mostrar(r.valor, decimales)}"
