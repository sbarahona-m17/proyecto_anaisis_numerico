"""Identidad visual y estilos de NumLab."""
from tkinter import ttk

MARINO = "#101e36"
MENTA = "#5ce6c3"
PALETAS = {
    False: dict(fondo="#eff3f9", papel="#ffffff", tinta="#172640",
                secundario="#52647a", borde="#d9e2ee", seleccion="#e0f5ee",
                acento="#086b57", alterna="#f1f5fa", panel="#e7edf6"),
    True: dict(fondo="#101827", papel="#172439", tinta="#edf4ff",
               secundario="#adbed3", borde="#30415b", seleccion="#1d423f",
               acento="#80e8ca", alterna="#1d2c43", panel="#131f31"),
}


def aplicar(estilo: ttk.Style, oscuro: bool) -> dict[str, str]:
    """Configura los estilos ttk y devuelve la paleta activa."""
    colores = PALETAS[oscuro]
    fondo, papel, tinta, secundario, borde, seleccion, acento, _, panel = colores.values()
    estilo.theme_use("clam")
    estilo.configure(".", background=fondo, foreground=tinta, font=("Segoe UI", 10),
                     troughcolor=panel, bordercolor=borde)
    estilo.configure("TFrame", background=fondo)
    estilo.configure("Panel.TFrame", background=papel)
    estilo.configure("Hero.TFrame", background=MARINO)
    estilo.configure("TButton", padding=(10, 5), background=papel, foreground=tinta,
                     lightcolor=papel, darkcolor=papel, relief="flat")
    estilo.map("TButton", background=[("active", seleccion), ("disabled", panel)],
               foreground=[("disabled", secundario)], bordercolor=[("focus", acento)])
    estilo.configure("Accion.TButton", background=MENTA, foreground="#103a35",
                     lightcolor=MENTA, darkcolor=MENTA, bordercolor=MENTA,
                     font=("Segoe UI Semibold", 10), padding=(14, 7))
    estilo.map("Accion.TButton", background=[("active", "#91f2d6"), ("disabled", panel)],
               bordercolor=[("focus", acento)], foreground=[("disabled", secundario)])
    estilo.configure("Barra.TButton", background="#213451", foreground="#eef5ff",
                     lightcolor="#213451", darkcolor="#213451", bordercolor="#334b6b")
    estilo.map("Barra.TButton", background=[("active", "#324c70")],
               bordercolor=[("focus", MENTA)])
    for nombre, fuente, tono in (
        ("Marca", ("Segoe UI Semibold", 14), MENTA),
        ("Hero", ("Segoe UI Semibold", 42), "#f6faff"),
        ("Subhero", ("Segoe UI Semibold", 17), "#e3edff"),
        ("DescripcionHero", ("Segoe UI", 11), "#b7c8e1"),
    ):
        estilo.configure(f"{nombre}.TLabel", background=MARINO, foreground=tono, font=fuente)
    estilo.configure("Titulo.TLabel", font=("Segoe UI Semibold", 21))
    estilo.configure("Resultado.TLabel", background=seleccion, foreground=acento,
                     font=("Segoe UI Semibold", 14))
    estilo.configure("Seccion.TLabel", font=("Segoe UI Semibold", 13))
    estilo.configure("Nota.TLabel", foreground=secundario)
    estilo.configure("Estado.TLabel", background=panel, foreground=secundario)
    estilo.configure("Tarjeta.TButton", anchor="w", font=("Segoe UI Semibold", 12),
                     padding=(13, 9), background=papel)
    estilo.configure("Treeview", background=papel, fieldbackground=papel,
                     foreground=tinta, rowheight=27, relief="flat")
    estilo.map("Treeview", background=[("selected", seleccion)],
               foreground=[("selected", acento)])
    estilo.configure("Treeview.Heading", font=("Segoe UI Semibold", 9),
                     background=panel, foreground=tinta, relief="flat", padding=(7, 5))
    estilo.configure("TNotebook", background=fondo, borderwidth=1)
    estilo.configure("TNotebook.Tab", background=panel, foreground=secundario,
                     padding=(9, 5), borderwidth=1)
    estilo.map("TNotebook.Tab", background=[("selected", papel), ("active", seleccion)],
               foreground=[("selected", acento)])
    for clase in ("TEntry", "TCombobox"):
        estilo.configure(clase, fieldbackground=papel, foreground=tinta,
                         insertcolor=tinta, padding=4)
        estilo.map(clase, fieldbackground=[("readonly", papel)],
                   foreground=[("readonly", tinta)], bordercolor=[("focus", acento)])
    return colores
