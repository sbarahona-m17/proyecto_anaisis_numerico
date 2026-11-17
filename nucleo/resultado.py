"""Contrato de resultados compartido."""
from dataclasses import dataclass, field


@dataclass
class Resultado:
    """Resultado, historial y metadatos de una ejecución."""
    valor: float | None
    convergio: bool
    mensaje: str
    tabla: list[dict] = field(default_factory=list)
    extra: dict = field(default_factory=dict)
