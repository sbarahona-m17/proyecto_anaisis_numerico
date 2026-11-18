"""Paletas y estilos de los controles de escritorio de NumLab."""
from tkinter import ttk

MARINO = "#152238"
MENTA = "#65dbcf"

PALETAS = {
    False: dict(fondo="#f1f4f8", papel="#ffffff", tinta="#17273c",
                secundario="#506178", borde="#d8e1ed", seleccion="#e5edff",
                acento="#244db7", alterna="#f5f7fb", panel="#eaf0f7"),
    True: dict(fondo="#111827", papel="#1b2639", tinta="#edf3fc",
               secundario="#afbdd0", borde="#34445c", seleccion="#293d63",
               acento="#a9c4ff", alterna="#202e44", panel="#162032"),
}

ACENTOS = {
    "Raíces": ("#3159ba", "#244fae", "#e8efff", "#b6cdff", "#293b60"),
    "Diferenciación": ("#13746a", "#116358", "#e1f4ef", "#91e1cf", "#244743"),
    "Interpolación": ("#7750ad", "#694399", "#f1eafb", "#d7baf8", "#403256"),
    "Integración": ("#a45724", "#884419", "#fcf0e3", "#f6c396", "#4e392f"),
    "EDO": ("#a34566", "#923654", "#fbeaf0", "#f4b5ca", "#503246"),
}


def acento_modulo(modulo: str | None, oscuro: bool) -> tuple[str, str]:
    """Devuelve el fondo suave y el texto de acento para la vista activa."""
    if modulo is None:
        paleta = PALETAS[oscuro]
        return paleta["seleccion"], paleta["acento"]
    _, texto_claro, fondo_claro, texto_oscuro, fondo_oscuro = ACENTOS[modulo]
    return (fondo_oscuro, texto_oscuro) if oscuro else (fondo_claro, texto_claro)


def aplicar(estilo: ttk.Style, oscuro: bool, modulo: str | None = None) -> dict[str, str]:
    """Aplica la paleta sin recrear los controles que contienen datos."""
    colores = PALETAS[oscuro]
    fondo, papel, tinta, secundario, borde, _, _, _, panel = colores.values()
    seleccion, acento = acento_modulo(modulo, oscuro)
    principal, enfoque = ACENTOS[modulo or "Raíces"][:2]
    lateral, texto_lateral = acento_modulo(modulo, True)
    estilo.theme_use("clam")
    estilo.configure(".", background=fondo, foreground=tinta, font=("Segoe UI", 10),
                     troughcolor=panel, bordercolor=borde, focuscolor=acento)
    estilo.configure("TFrame", background=fondo)
    estilo.configure("Panel.TFrame", background=papel)
    estilo.configure("Tarjeta.TFrame", background=papel, bordercolor=borde,
                     borderwidth=1, relief="solid")
    estilo.configure("Hero.TFrame", background=MARINO)
    estilo.configure("TButton", padding=(10, 5), background=papel, foreground=tinta,
                     lightcolor=papel, darkcolor=papel, borderwidth=1, relief="flat")
    estilo.map("TButton", background=[("disabled", panel), ("active", seleccion)],
               foreground=[("disabled", secundario)], bordercolor=[("focus", acento)])
    estilo.configure("Accion.TButton", background=principal, foreground="#ffffff",
                     lightcolor=principal, darkcolor=principal, bordercolor=principal,
                     focuscolor="#ffffff", font=("Segoe UI Semibold", 10), padding=(14, 8))
    estilo.map("Accion.TButton", background=[("disabled", panel), ("active", enfoque)],
               foreground=[("disabled", secundario)])
    estilo.configure("Barra.TButton", anchor="w", padding=(11, 8),
                     background=MARINO, foreground="#e3ecfa", borderwidth=0,
                     focuscolor=MENTA, font=("Segoe UI Semibold", 10))
    estilo.map("Barra.TButton", background=[("selected", lateral), ("active", "#20344f")],
               foreground=[("selected", texto_lateral)])
    estilo.configure("Compacto.TButton", padding=(6, 3), font=("Segoe UI", 9))
    estilo.layout("Metodo.TRadiobutton", estilo.layout("TButton"))
    estilo.configure("Metodo.TRadiobutton", background=papel, foreground=tinta,
                     anchor="center", borderwidth=1, relief="flat", padding=(10, 7),
                     font=("Segoe UI Semibold", 10))
    estilo.map("Metodo.TRadiobutton",
               background=[("selected", seleccion), ("active", panel)],
               foreground=[("selected", acento)],
               bordercolor=[("selected", acento), ("focus", acento)])
    for nombre, fuente, tono in (
        ("Marca", ("Segoe UI Semibold", 18), "#ffffff"),
        ("Hero", ("Segoe UI Semibold", 26), "#f6faff"),
        ("DescripcionHero", ("Segoe UI", 11), "#c4d2e7"),
    ):
        estilo.configure(f"{nombre}.TLabel", background=MARINO, foreground=tono, font=fuente)
    estilo.configure("Titulo.TLabel", font=("Segoe UI Semibold", 20))
    estilo.configure("Acento.TFrame", background=seleccion)
    estilo.configure("FormularioTitulo.TLabel", background=seleccion, foreground=acento,
                     font=("Segoe UI Semibold", 13))
    estilo.configure("Grupo.TLabel", background=papel, foreground=acento,
                     font=("Segoe UI Semibold", 10))
    estilo.configure("Resultado.TLabel", background=seleccion, foreground=acento,
                     font=("Segoe UI Semibold", 15))
    estilo.configure("ResultadoNota.TLabel", background=seleccion, foreground=tinta)
    estilo.configure("Seccion.TLabel", font=("Segoe UI Semibold", 12))
    estilo.configure("Panel.TLabel", background=papel)
    estilo.configure("PanelNota.TLabel", background=papel, foreground=secundario)
    estilo.configure("PanelTitulo.TLabel", background=papel, font=("Segoe UI Semibold", 12))
    estilo.configure("Campo.TLabel", background=papel, foreground=secundario,
                     font=("Segoe UI Semibold", 9))
    estilo.configure("Nota.TLabel", foreground=secundario)
    estilo.configure("Estado.TLabel", background=panel, foreground=secundario,
                     font=("Segoe UI", 9))
    estilo.configure("Tarjeta.TButton", anchor="w", font=("Segoe UI Semibold", 11),
                     padding=(4, 4), background=papel, borderwidth=0)
    estilo.configure("Treeview", background=papel, fieldbackground=papel,
                     foreground=tinta, rowheight=26, relief="flat", borderwidth=0)
    estilo.map("Treeview", background=[("selected", seleccion)],
               foreground=[("selected", acento)])
    estilo.configure("Treeview.Heading", font=("Segoe UI Semibold", 9),
                     background=panel, foreground=tinta, relief="flat", padding=(7, 5))
    estilo.configure("TNotebook", background=papel, borderwidth=0, tabmargins=(5, 3, 5, 0))
    estilo.configure("TNotebook.Tab", background=papel, foreground=secundario,
                     padding=(8, 5), borderwidth=0, font=("Segoe UI Semibold", 9))
    estilo.map("TNotebook.Tab", background=[("selected", seleccion), ("active", panel)],
               foreground=[("selected", acento)])
    estilo.configure("Espacio.TNotebook.Tab", padding=(14, 6), font=("Segoe UI Semibold", 10))
    estilo.configure("TCheckbutton", padding=(4, 4), focusthickness=1)
    for clase in ("TEntry", "TCombobox"):
        estilo.configure(clase, fieldbackground=papel, foreground=tinta,
                         insertcolor=tinta, padding=(6, 4))
        estilo.map(clase, fieldbackground=[("readonly", papel)],
                   foreground=[("readonly", tinta)], bordercolor=[("focus", acento)])
    estilo.configure("Expresion.TEntry", fieldbackground=seleccion, font=("Consolas", 11),
                     padding=(7, 6))
    return colores
