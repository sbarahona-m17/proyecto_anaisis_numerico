"""Datos de entrada de la sección 11 de la guía oficial."""
RAICES = ("Bisección", "Falsa posición", "Newton-Raphson", "Secante")
DERIVACION = ("Primera derivada", "Segunda derivada")
INTERPOLACION = ("Lagrange", "Newton")

D2 = list(zip([1, 1.5, 2, 2.5, 3], [557.5, 583.8125, 612, 641.6875, 672.5]))
I1 = list(zip([1, 2, 4, 8], [120, 210, 350, 480]))
I2 = list(zip([0.5, 1, 2, 3, 4], [42, 55, 81, 118, 170]))
N3 = list(zip(range(0, 61, 10), [120, 180, 260, 310, 280, 210, 150]))

EJEMPLOS = {
    "Raíces": {
        "R-1 · Dimensionamiento de un clúster": dict(f="x^3-2x-5", a=2, b=3, x0=2.5, s0=2, s1=3),
        "R-2 · Equilibrio de una caché": dict(f="exp(-x)-x", a=0, b=1, x0=.5, s0=0, s1=1),
        "R-3 · Ley de Amdahl": dict(f="1/(0.1+0.9/x)-4", a=2, b=10, x0=3, s0=2, s1=10, referencia=6),
        "R-4a · Sin cambio de signo": dict(f="x^2+1", a=-1, b=1),
        "R-4b · Oscilación": dict(f="x^3-2x+2", x0=0, metodo="Newton-Raphson"),
        "R-4c · Derivada nula": dict(f="x^2-4", x0=0, metodo="Newton-Raphson"),
        "R-4d · Semilla alternativa": dict(f="x^3-2x+2", x0=-2, metodo="Newton-Raphson"),
    },
    "Diferenciación": {
        **{f"D-1 · Carga de CPU (h={h})": dict(f="20+15sin(x/2)+0.3*x^2", x0=4, h=h)
           for h in (.5, .1, .01)},
        "D-2 · Consumo de memoria": dict(modo="Tabla", datos=D2),
        "D-3 · Exponencial trigonométrica": dict(f="exp(x)*sin(x)", x0=1, h=.1),
    },
    "Interpolación": {
        "I-1 · Rendimiento por hilos": dict(datos=I1, consultas=6),
        "I-2 · Tiempo de respuesta de API": dict(datos=I2, consultas=2.5),
    },
    "Integración": {
        **{f"N-1 · Integral de referencia (n={n})": dict(f="1/(1+x^2)", a=0, b=1, n=n)
           for n in (4, 10)},
        **{f"N-2 · Energía de un centro de datos (n={n})": dict(
            f="250+40*x*exp(-0.3*x)", a=0, b=8, n=n) for n in (4, 8)},
        "N-3 · Transferencia de datos": dict(modo="Tabla", datos=N3,
                                            unidad="Minutos y Mbps", metodo="Trapecio compuesto"),
    },
    "EDO": {
        "E-1 · Adopción de una aplicación": dict(f="0.8y(1-y/1000)", t0=0, y0=50, tf=5,
                                                h=.5, exacta="1000/(1+19*exp(-0.8*t))"),
        "E-2 · Caso clásico": dict(f="y-t^2+1", t0=0, y0=.5, tf=2,
                                   h=.2, exacta="(t+1)^2-0.5*exp(t)"),
    },
}
