# Guía de sustentación

## Guion de 18 minutos

| Minutos | Segmento | Demostración |
|---:|---|---|
| 0–2 | Contexto y objetivo | Presentar la pantalla inicial y el recorrido método → datos → resultados |
| 2–5 | Raíces | Abrir R-3, mostrar la primera fila, animar y comparar. Probar el ciclo de R-4b |
| 5–8 | Diferenciación | Comparar D-1 con h=0.5 y 0.1. Explicar el log-log y cargar D-2 |
| 8–10 | Interpolación | Abrir I-2. Mostrar el cero de la tabla triangular y comparar expresiones |
| 10–13 | Integración | Comparar N-2 y revisar parábolas. Mostrar unidades en N-3 |
| 13–16 | EDO | Comparar E-1, mostrar las pendientes y el refinamiento h/2 |
| 16–18 | Ingeniería y verificación | Mostrar Resultado, parser, pruebas y una exportación |

## Preguntas y respuestas

**¿Dónde se actualiza el intervalo en falsa posición?** En `nucleo/raices.py`, dentro de `_resolver`. Si f(a) y f(c) difieren de signo se reemplaza b. En el otro caso se reemplaza a. La salida por raíz exacta ocurre antes de actualizar.

**¿En qué difieren bisección y falsa posición?** Bisección elige el punto medio, reduciendo la longitud a la mitad. Falsa posición corta la secante de los extremos con el eje x. Puede dejar fijo un extremo.

**¿Qué ocurre si f′(xₙ) vale cero en Newton?** El cociente no es utilizable. El algoritmo devuelve la última aproximación y explica la detención. Si f ya valía cero, termina por raíz exacta antes de dividir.

**¿Qué estima secante?** Una pendiente con dos puntos recientes. Si sus evaluaciones coinciden el denominador es cero. Newton utiliza una derivada en un solo punto.

**¿Por qué las fórmulas de cinco puntos son de orden cuatro?** Los pesos se eligen para cancelar términos de series de Taylor. En la primera derivada el primer término restante escala como h⁴f⁽⁵⁾; para la segunda escala como h⁴f⁽⁶⁾, con la suavidad necesaria. Al hacer h diminuto pesan más el redondeo y la cancelación.

**¿Qué es la tabla de diferencias divididas?** Un triángulo cuyos elementos se construyen con diferencias de orden inferior divididas por la distancia entre sus abscisas extremas. La primera fila suministra los coeficientes de Newton.

**¿Por qué Lagrange y Newton dan el mismo polinomio?** Los dos satisfacen las mismas n+1 condiciones y tienen grado máximo n. Su diferencia se anula en n+1 puntos y por tanto es idénticamente cero.

**¿Por qué Simpson compuesto exige n par?** Cada parábola ocupa dos subintervalos y usa tres nodos. Con n impar quedaría uno sin pareja.

**¿Cuál es la diferencia entre Euler, Heun y RK4?** Euler evalúa la pendiente inicial. Heun añade una evaluación final en el punto predicho y promedia. RK4 combina cuatro etapas. Sus órdenes globales son uno, dos y cuatro.

**¿Qué ventaja tiene RK4?** Para una solución suave y un paso dentro de la región de estabilidad, logra menor error global a un mismo h. El costo aumenta a cuatro evaluaciones de f por paso.

**¿Qué representa el error absoluto y relativo?** El absoluto está en las unidades del resultado. El relativo se normaliza dividiendo por el valor absoluto de la referencia y suele expresarse en porcentaje. Si la referencia es cero, el porcentaje no está definido.

**¿Cómo se separa la lógica de la interfaz?** Los algoritmos reciben funciones o datos, devuelven `Resultado` y se prueban sin ventanas. La capa de interfaz decide cómo mostrarlo y captura errores. La capa de gráficas toma los resultados y construye artistas de Matplotlib.

**¿Por qué la entrada de funciones no ejecuta Python?** La gramática acepta tokens explícitos, construye árboles SymPy sin interpretar código de Python y evalúa operaciones desde un conjunto fijo.

## Práctica individual

Cada integrante debe recorrer el código que va a explicar, demostrar un caso propio y practicar una falla de dominio, un n impar y una extrapolación. Tener a mano `python -m pytest -v`, la guía institucional y las evidencias del equipo.
