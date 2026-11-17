"""Campos del módulo de raíces."""
CAMPOS = (
    ("f", "Función f(x)", "x^3-2x-5"),
    ("a", "Intervalo · extremo inferior a", "2"),
    ("b", "Intervalo · extremo superior b", "3"),
    ("x0", "Newton · aproximación inicial", "2.5"),
    ("s0", "Secante · primera aproximación", "2"),
    ("s1", "Secante · segunda aproximación", "3"),
    ("tol", "Tolerancia (en % si es relativa)", "1e-6"),
    ("max_iter", "Máximo de iteraciones", "100"),
    ("criterio", "Criterio de parada", ("Absoluto", "Relativo (%)", "Residuo")),
    ("referencia", "Raíz exacta conocida (opcional)", ""),
)


def visibles(metodo: str, campos: dict, comparar: bool) -> set[str]:
    """Selecciona las semillas que requiere el cálculo."""
    semillas = {"a", "b", "x0", "s0", "s1"} if comparar else {
        "Bisección": {"a", "b"}, "Falsa posición": {"a", "b"},
        "Newton-Raphson": {"x0"}, "Secante": {"s0", "s1"},
    }[metodo]
    return semillas | {"f", "tol", "max_iter", "criterio", "referencia"}
