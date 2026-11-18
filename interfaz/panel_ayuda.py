"""Ayuda contextual con teoría de todos los métodos."""
import tkinter as tk
from tkinter import ttk

GENERAL = """Selecciona un módulo y un método. Puedes comenzar con un ejemplo oficial o introducir datos propios.
    
Escribe funciones con punto decimal. Usa x para funciones de una variable y t, y para ecuaciones diferenciales. Puedes usar ^, multiplicación implícita, sin, cos, tan, exp, ln, log, sqrt, abs, pi y e. Ejemplo: 20+15sin(x/2).

Para editar datos, haz doble clic sobre una celda y confirma con Intro. Puedes importar dos columnas desde un CSV UTF-8. En interpolación separa las consultas con espacios.

Comparación activa los métodos del mismo módulo. En diferenciación, las dos filas corresponden a órdenes distintos de derivada. En la pestaña de gráfica, la barra inferior permite restaurar, mover, ampliar y guardar. En las escalas logarítmicas se omiten los errores de valor cero.

El error relativo porcentual divide el error absoluto por la magnitud de la referencia. Si la referencia vale cero, el porcentaje aparece como no disponible."""
TEORIA = {
    "Bisección": (
        "c = (a+b)/2. a y b son los extremos y c es el punto medio.",
        "Evalúa f(c) y, si no es cero, conserva la mitad con signos opuestos.",
        "Requiere continuidad en [a,b] y signos opuestos, salvo raíz en un extremo.",
        "El intervalo se reduce a la mitad en cada paso. Puede requerir muchas evaluaciones y un salto de la función puede aparentar un cambio de signo."),
    "Falsa posición": (
        "c = (a·f(b) − b·f(a))/(f(b) − f(a)). a y b encierran la raíz.",
        "Corta con el eje la secante entre extremos y conserva el cambio de signo.",
        "Usa una función continua con signos opuestos en los extremos.",
        "Aprovecha las ordenadas. Un extremo puede quedar fijo y ralentizar el proceso."),
    "Newton-Raphson": (
        "x siguiente = x − f(x)/f′(x). x es la aproximación actual.",
        "Calcula la derivada simbólica y corta la tangente con el eje horizontal.",
        "Conviene iniciar cerca de una raíz simple con derivada no nula.",
        "La convergencia local puede ser cuadrática. Una mala semilla puede producir ciclos o salir del dominio."),
    "Secante": (
        "x siguiente = xₙ − f(xₙ)(xₙ−x anterior)/(f(xₙ)−f(x anterior)).",
        "Estima la pendiente con dos aproximaciones y desplaza ambas semillas.",
        "Usa puntos distintos y ordenadas distintas durante el paso.",
        "Evita derivar y suele converger rápido cerca de una raíz simple. Puede salir del dominio o estancarse."),
    "Primera derivada": (
        "f′(x₀) ≈ [f(x₀−2h)−8f(x₀−h)+8f(x₀+h)−f(x₀+2h)]/(12h).",
        "Suma los valores ponderados de los nodos vecinos y divide por 12h.",
        "Necesita cinco nodos uniformes y h>0. El orden cuatro requiere derivadas suficientemente suaves.",
        "La primera derivada estima la pendiente de la tangente. Un paso muy pequeño amplifica el redondeo."),
    "Segunda derivada": (
        "f″(x₀) ≈ [−f(x₀−2h)+16f(x₀−h)−30f(x₀)+16f(x₀+h)−f(x₀+2h)]/(12h²).",
        "Suma los valores ponderados de los cinco nodos y divide por 12h².",
        "Necesita cinco nodos uniformes y h>0. El orden cuatro requiere derivadas suficientemente suaves.",
        "La segunda derivada mide el cambio de pendiente. La división por h² amplifica el redondeo."),
    "Lagrange": (
        "P(x)=Σ yᵢLᵢ(x), con Lᵢ(x)=Πⱼ≠ᵢ [(x−xⱼ)/(xᵢ−xⱼ)].",
        "Construye una base por nodo, multiplícala por yᵢ y suma.",
        "Las abscisas xᵢ deben ser distintas. Se evalúa en la consulta x*.",
        "Cada base muestra la contribución de su nodo. Agregar nodos obliga a reconstruir las bases y extrapolar puede amplificar errores."),
    "Newton": (
        "Dᵢ,ₖ = (Dᵢ₊₁,ₖ₋₁−Dᵢ,ₖ₋₁)/(xᵢ₊ₖ−xᵢ), con Dᵢ,₀=yᵢ.",
        "Construye el triángulo y multiplica D₀,ₖ por los primeros k factores (x−xⱼ).",
        "Usa abscisas distintas. El orden de los nodos cambia la forma, con el mismo polinomio exacto.",
        "Facilita añadir un nodo. Muchos nodos o nodos cercanos pueden degradar la evaluación numérica."),
    "Trapecio simple": (
        "I ≈ (b−a)[f(a)+f(b)]/2. a y b delimitan el intervalo.",
        "Une los extremos con una recta e integra la figura.",
        "Necesita a<b y valores finitos en ambos extremos.",
        "Solo utiliza dos puntos. La curvatura en intervalos amplios puede producir error grande."),
    "Trapecio compuesto": (
        "I ≈ h[ f(a) + 2Σ f(xᵢ) + f(b) ]/2. h=(b−a)/n.",
        "Suma las áreas de n trapecios con nodos uniformes.",
        "n es entero positivo y los datos deben estar equiespaciados.",
        "Usa cualquier n válido. El error global es O(h²) bajo las hipótesis de suavidad."),
    "Simpson 1/3 simple": (
        "I ≈ (b−a)[f(a)+4f((a+b)/2)+f(b)]/6.",
        "Ajusta una parábola con los extremos y su punto medio.",
        "Necesita tres evaluaciones equiespaciadas. Si usa una tabla, debe existir un nodo medido en el punto medio.",
        "Es exacto para polinomios hasta grado tres. Un tramo puede representar pobremente funciones con curvatura variable."),
    "Simpson 1/3 compuesto": (
        "I ≈ h[ f(a)+4Σ impares +2Σ pares interiores +f(b)]/3.",
        "Integra una parábola por cada par de subintervalos, con h=(b−a)/n.",
        "n debe ser par y al menos dos, con nodos equiespaciados.",
        "El error global es O(h⁴) para funciones suaves. Los pesos requieren la malla compatible."),
    "Euler": (
        "y siguiente = y + h·f(t,y), donde h es el paso temporal.",
        "Avanza con la pendiente inicial de cada tramo.",
        "Usa un problema y′=f(t,y) con condición inicial y paso positivo.",
        "Una evaluación por paso. Su error global es de orden uno y un paso grande puede causar inestabilidad."),
    "Heun": (
        "Predictor y*=y+h·f(t,y). Corrector y siguiente=y+h[f(t,y)+f(t+h,y*)]/2.",
        "Promedia la pendiente inicial y la evaluada en el punto predicho.",
        "Usa un problema de valor inicial y dos evaluaciones finitas por paso.",
        "Orden global dos para problemas suaves. Conserva restricciones de estabilidad de los métodos explícitos."),
    "Runge-Kutta 4": (
        "y siguiente=y+h(k1+2k2+2k3+k4)/6.",
        "k1 se toma al inicio; k2 y k3 se toman a medio paso con las pendientes previas; k4 se toma al final con k3.",
        "Requiere un paso positivo y evaluaciones finitas en las cuatro etapas.",
        "Orden global cuatro para problemas suaves. Cuatro evaluaciones por paso y sensibilidad a rigidez o pasos grandes."),
}


def abrir(master: tk.Misc, colores: dict, metodo: str | None = None) -> None:
    """Abre ayuda general o teoría del método seleccionado."""
    ventana = tk.Toplevel(master)
    ventana.title(f"NumLab · {metodo or 'Ayuda general'}")
    ventana.geometry("630x450")
    ventana.transient(master)
    ttk.Label(ventana, text=metodo or "Cómo usar NumLab", style="Titulo.TLabel").pack(
        anchor="w", padx=18, pady=(15, 8))
    contenedor = ttk.Frame(ventana)
    contenedor.pack(fill="both", expand=True, padx=18, pady=8)
    texto = tk.Text(contenedor, wrap="word", font=("Segoe UI", 11),
                    background=colores["papel"], foreground=colores["tinta"],
                    padx=15, pady=12, relief="flat")
    scroll = ttk.Scrollbar(contenedor, command=texto.yview)
    texto.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    texto.pack(side="left", fill="both", expand=True)
    contenido = GENERAL if metodo is None else "\n\n".join(
        f"{titulo}\n{parte}" for titulo, parte in zip(
            ("Fórmula y variables", "Procedimiento", "Condiciones", "Ventajas y limitaciones"),
            TEORIA[metodo]))
    texto.insert("1.0", contenido)
    texto.configure(state="disabled")
    ttk.Button(ventana, text="Volver", command=ventana.destroy).pack(pady=(0, 10))
