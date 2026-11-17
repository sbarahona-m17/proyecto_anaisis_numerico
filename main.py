"""Punto de entrada de NumLab."""
from multiprocessing import freeze_support


def main() -> None:
    """Inicia la aplicación de escritorio."""
    from interfaz.ventana_principal import Aplicacion

    Aplicacion().mainloop()


if __name__ == "__main__":
    freeze_support()
    main()
