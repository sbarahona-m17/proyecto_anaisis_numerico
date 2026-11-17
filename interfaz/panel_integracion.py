"""Campos de cuadratura."""
CAMPOS = (
    ("modo", "Origen", ("Función", "Tabla")),
    ("f", "Función f(x)", "1/(1+x^2)"),
    ("a", "Límite inferior a", "0"),
    ("b", "Límite superior b", "1"),
    ("n", "Subintervalos n (par para Simpson)", "4"),
    ("unidad", "Unidades", ("Originales", "Minutos y Mbps")),
)


def visibles(metodo: str, campos: dict, comparar: bool) -> set[str]:
    """Presenta los límites y el número de subintervalos solo si se usan."""
    claves = {"modo", "unidad"}
    if campos["modo"] == "Función":
        claves.update(("f", "a", "b"))
        if comparar or metodo.endswith("compuesto"):
            claves.add("n")
    return claves
