"""Campos de problemas de valor inicial."""
CAMPOS = (
    ("f", "Función f(t, y)", "0.8y(1-y/1000)"),
    ("t0", "Tiempo inicial t₀", "0"),
    ("y0", "Condición inicial y₀", "50"),
    ("tf", "Tiempo final tᶠ", "5"),
    ("paso", "Configuración de la malla", ("Tamaño de paso h", "Número de pasos N")),
    ("h", "Tamaño de paso h", ".5"),
    ("n", "Número de pasos N", "10"),
    ("exacta", "Referencia exacta y(t), opcional", ""),
)


def visibles(metodo: str, campos: dict, comparar: bool) -> set[str]:
    """Muestra el parámetro activo de la malla."""
    clave = "h" if campos["paso"] == "Tamaño de paso h" else "n"
    return {"f", "t0", "y0", "tf", "paso", "exacta", clave}
