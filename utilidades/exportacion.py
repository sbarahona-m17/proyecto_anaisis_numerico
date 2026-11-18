"""Lectura y escritura CSV de NumLab."""
import csv
from pathlib import Path

from utilidades.validaciones import nodos


def columnas(filas: list[dict]) -> list[str]:
    """Conserva el orden de aparición de todas las columnas."""
    return list(dict.fromkeys(clave for fila in filas for clave in fila))


def leer_csv(ruta: str | Path) -> list[tuple[float, float]]:
    """Lee dos columnas separadas por coma o punto y coma, con encabezado opcional."""
    try:
        with open(ruta, encoding="utf-8-sig", newline="") as archivo:
            muestra = archivo.read(4096)
            if not muestra.strip():
                raise ValueError("El archivo CSV está vacío.")
            archivo.seek(0)
            primera_fila = next(fila for fila in muestra.splitlines() if fila.strip())
            delimitador = ";" if ";" in primera_fila else ","
            filas = []
            for fila in csv.reader(archivo, delimiter=delimitador, strict=True):
                if any(celda.strip() for celda in fila):
                    filas.append(fila)
                    if len(filas) > 10002:
                        raise ValueError("El CSV supera el límite de 10 001 nodos.")
    except (csv.Error, UnicodeError) as error:
        raise ValueError("CSV mal formado o con una codificación distinta de UTF-8.") from error
    encabezados = {("x", "y"), ("x", "f(x)"), ("t", "y"), ("t", "tasa"),
                   ("tiempo", "tasa"), ("minutos", "mbps")}
    if filas and tuple(c.strip().lower() for c in filas[0]) in encabezados:
        filas.pop(0)
    if not filas:
        raise ValueError("El CSV no contiene datos.")
    return nodos(filas)


def guardar_csv(ruta: str | Path, filas: list[dict]) -> None:
    """Exporta los valores sin aplicar el redondeo de pantalla."""
    if not filas:
        raise ValueError("La tabla seleccionada está vacía.")
    with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas(filas))
        escritor.writeheader()
        escritor.writerows(filas)
