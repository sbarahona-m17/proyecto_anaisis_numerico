"""Campos de diferenciación centrada."""
CAMPOS = (
    ("modo", "Origen", ("Función", "Tabla")),
    ("f", "Función f(x)", "20+15sin(x/2)+0.3*x^2"),
    ("x0", "Punto central x₀", "4"),
    ("h", "Distancia entre nodos h", ".1"),
)


def visibles(metodo: str, campos: dict, comparar: bool) -> set[str]:
    """Alterna los campos analíticos y los nodos medidos."""
    return {"modo"} if campos["modo"] == "Tabla" else {"modo", "f", "x0", "h"}
