"""Campos de interpolación."""
CAMPOS = (("consultas", "Evaluar x* (separe con espacios)", "6"),)


def visibles(metodo: str, campos: dict, comparar: bool) -> set[str]:
    """Conserva el campo de evaluación para ambos métodos."""
    return {"consultas"}
