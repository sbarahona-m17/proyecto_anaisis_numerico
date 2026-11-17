"""Representación de valores para pantalla y reporte."""


def mostrar(valor: object, decimales: int = 8) -> str:
    """Formatea ausencias y usa notación científica para valores diminutos."""
    if valor is None:
        return "No disponible"
    if isinstance(valor, float):
        if valor and (abs(valor) < 10**-decimales or abs(valor) >= 1e9):
            return f"{valor:.{decimales}e}"
        return f"{valor:.{decimales}f}"
    return str(valor)
