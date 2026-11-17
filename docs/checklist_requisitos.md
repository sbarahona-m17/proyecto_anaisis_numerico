# Matriz de trazabilidad

La verificación corresponde a la instalación de desarrollo en Windows. Las pruebas gráficas ejecutan Tkinter y dibujan las vistas en el entorno local. Las pruebas de archivo usan rutas temporales. La entrega institucional se registra en [Evidencias](evidencias.md).

| Requisito | Descripción | Archivo de implementación | Prueba asociada | Estado |
|---|---|---|---|---|
| RG-1 | Inicio, cinco módulos y selector | interfaz/ventana_principal.py | tests/test_interfaz.py | Implementado y verificado |
| RG-2 | Funciones, tabla editable y CSV | utilidades/parser.py, interfaz/tabla_resultados.py | tests/test_interfaz.py, tests/test_parser.py | Implementado y verificado |
| RG-3 | Validación de tipo, rango, dominio y entradas | utilidades/validaciones.py y nucleo/ | Suite numérica y prueba de recuperación | Implementado y verificado |
| RG-4 | Tolerancia, iteraciones, paso, n y decimales | interfaz/panel_*.py | tests/test_interfaz.py y suite numérica | Implementado y verificado |
| RG-5 | Tablas desplazables y encabezados | interfaz/tabla_resultados.py | tests/test_interfaz.py | Implementado y verificado |
| RG-6 | Figuras incrustadas, ejes, leyenda, cuadrícula y herramientas | interfaz/panel_graficas.py, graficas/ | tests/test_interfaz.py y revisión visual en Windows | Implementado y verificado |
| RG-7 | Error absoluto, relativo y de referencia | utilidades/errores.py | tests/test_validaciones.py y suite numérica | Implementado y verificado |
| RG-8 | Exportación CSV y PNG | interfaz/ventana_principal.py, utilidades/exportacion.py | tests/test_interfaz.py | Implementado y verificado |
| RG-9 | Ayuda general y contextual con teoría | interfaz/panel_ayuda.py | Revisión de contenido y prueba de apertura | Implementado y verificado |
| RG-10 | Calcular, Limpiar, Volver y ejemplos | interfaz/ventana_principal.py, utilidades/ejemplos.py | tests/test_interfaz.py | Implementado y verificado |
| RG-11 | Comparación en todos los módulos | utilidades/comparaciones.py | tests/test_comparaciones.py, tests/test_interfaz.py | Implementado y verificado |
| RNF-1 | Rechazo recuperable en casos de robustez | nucleo/ y utilidades/ | Suite numérica y prueba de recuperación | Implementado y verificado |
| RNF-2 | Español, valores iniciales y diseño adaptable | interfaz/ | Pruebas Tk y revisión visual | Implementado y verificado |
| RNF-3 | Capas, docstrings, tipos y estilo PEP 8 | nucleo/, interfaz/, graficas/, utilidades/ | Imports y revisión de estructura. Auditoría completa de estilo pendiente | Implementado sin verificar |
| RNF-4 | pytest para cada algoritmo | tests/ | python -m pytest -v | Implementado y verificado |
| RNF-5 | Instalación y arranque | main.py, requirements.txt | pip y ventana activa en Windows | Implementado y verificado |
| raices-1 | Bisección | nucleo/raices.py | tests/test_raices.py | Implementado y verificado |
| raices-2 | Falsa posición | nucleo/raices.py | tests/test_raices.py | Implementado y verificado |
| raices-3 | Newton-Raphson | nucleo/raices.py | tests/test_raices.py | Implementado y verificado |
| raices-4 | Secante | nucleo/raices.py | tests/test_raices.py | Implementado y verificado |
| derivacion-1 | Primera derivada de cinco puntos | nucleo/derivacion.py | tests/test_derivacion.py | Implementado y verificado |
| derivacion-2 | Segunda derivada de cinco puntos | nucleo/derivacion.py | tests/test_derivacion.py | Implementado y verificado |
| interpolacion-1 | Lagrange | nucleo/interpolacion.py | tests/test_interpolacion.py | Implementado y verificado |
| interpolacion-2 | Newton por diferencias divididas | nucleo/interpolacion.py | tests/test_interpolacion.py | Implementado y verificado |
| integracion-1 | Trapecio simple | nucleo/integracion.py | tests/test_integracion.py | Implementado y verificado |
| integracion-2 | Trapecio compuesto | nucleo/integracion.py | tests/test_integracion.py | Implementado y verificado |
| integracion-3 | Simpson 1/3 simple | nucleo/integracion.py | tests/test_integracion.py | Implementado y verificado |
| integracion-4 | Simpson 1/3 compuesto | nucleo/integracion.py | tests/test_integracion.py | Implementado y verificado |
| edo-1 | Euler | nucleo/edo.py | tests/test_edo.py | Implementado y verificado |
| edo-2 | Heun | nucleo/edo.py | tests/test_edo.py | Implementado y verificado |
| edo-3 | Runge-Kutta 4 | nucleo/edo.py | tests/test_edo.py | Implementado y verificado |
| G-raices-1 | Función, aproximaciones y raíz | graficas/grafica_raices.py | tests/test_interfaz.py | Implementado y verificado |
| G-raices-2 | Geometría de intervalos, tangentes y secantes | graficas/grafica_raices.py | tests/test_interfaz.py | Implementado y verificado |
| G-raices-3 | Convergencia semilogarítmica | graficas/grafica_raices.py | tests/test_interfaz.py | Implementado y verificado |
| G-derivacion-1 | Función, cinco puntos y tangente | graficas/grafica_derivacion.py | tests/test_interfaz.py | Implementado y verificado |
| G-derivacion-2 | Error frente a h en log-log | graficas/grafica_derivacion.py | tests/test_interfaz.py | Implementado y verificado |
| G-interpolacion-1 | Curva, nodos y estimaciones | graficas/grafica_interpolacion.py | tests/test_interfaz.py | Implementado y verificado |
| G-interpolacion-2 | Bases de Lagrange | graficas/grafica_interpolacion.py | tests/test_interfaz.py | Implementado y verificado |
| G-interpolacion-3 | Parciales de Newton | graficas/grafica_interpolacion.py | tests/test_interfaz.py | Implementado y verificado |
| G-integracion-1 | Curva y área | graficas/grafica_integracion.py | tests/test_interfaz.py | Implementado y verificado |
| G-integracion-2 | Trapecios sombreados | graficas/grafica_integracion.py | tests/test_interfaz.py | Implementado y verificado |
| G-integracion-3 | Parábolas de Simpson | graficas/grafica_integracion.py | tests/test_interfaz.py | Implementado y verificado |
| G-integracion-4 | Áreas superpuestas | graficas/grafica_integracion.py | tests/test_interfaz.py | Implementado y verificado |
| G-integracion-5 | Error frente a n en log-log | graficas/grafica_integracion.py | tests/test_interfaz.py | Implementado y verificado |
| G-edo-1 | Trayectorias y exacta | graficas/grafica_edo.py | tests/test_interfaz.py | Implementado y verificado |
| G-edo-2 | Errores semilogarítmicos | graficas/grafica_edo.py | tests/test_interfaz.py | Implementado y verificado |
| G-edo-3 | Campo de pendientes quiver | graficas/grafica_edo.py | tests/test_interfaz.py | Implementado y verificado |
| R-1 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_raices.py, tests/test_interfaz.py | Implementado y verificado |
| R-2 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_raices.py, tests/test_interfaz.py | Implementado y verificado |
| R-3 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_raices.py, tests/test_interfaz.py | Implementado y verificado |
| R-4a | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_raices.py, tests/test_interfaz.py | Implementado y verificado |
| R-4b | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_raices.py, tests/test_interfaz.py | Implementado y verificado |
| R-4c | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_raices.py, tests/test_interfaz.py | Implementado y verificado |
| R-4d | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_raices.py, tests/test_interfaz.py | Implementado y verificado |
| D-1 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_derivacion.py, tests/test_interfaz.py | Implementado y verificado |
| D-2 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_derivacion.py, tests/test_interfaz.py | Implementado y verificado |
| D-3 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_derivacion.py, tests/test_interfaz.py | Implementado y verificado |
| I-1 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_interpolacion.py, tests/test_interfaz.py | Implementado y verificado |
| I-2 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_interpolacion.py, tests/test_interfaz.py | Implementado y verificado |
| N-1 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_integracion.py, tests/test_interfaz.py | Implementado y verificado |
| N-2 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_integracion.py, tests/test_interfaz.py | Implementado y verificado |
| N-3 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_integracion.py, tests/test_interfaz.py | Implementado y verificado |
| E-1 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_edo.py, tests/test_interfaz.py | Implementado y verificado |
| E-2 | Datos de la guía, salida o detención esperada | utilidades/ejemplos.py | tests/test_edo.py, tests/test_interfaz.py | Implementado y verificado |
| C-Raíces | Cuatro métodos con aislamiento de fallos | utilidades/comparaciones.py | tests/test_interfaz.py, tests/test_comparaciones.py | Implementado y verificado |
| C-Diferenciación | Errores de ambas magnitudes por separado | utilidades/comparaciones.py | tests/test_interfaz.py, tests/test_comparaciones.py | Implementado y verificado |
| C-Interpolación | Equivalencia simbólica y numérica | utilidades/comparaciones.py | tests/test_interfaz.py, tests/test_comparaciones.py | Implementado y verificado |
| C-Integración | Cuatro reglas y errores frente a n | utilidades/comparaciones.py | tests/test_interfaz.py, tests/test_comparaciones.py | Implementado y verificado |
| C-EDO | Tres trayectorias y refinamiento h/2 | utilidades/comparaciones.py | tests/test_interfaz.py, tests/test_comparaciones.py | Implementado y verificado |
| CSV entrada | Lectura y edición de nodos | utilidades/exportacion.py | tests/test_interfaz.py, tests/test_validaciones.py | Implementado y verificado |
| CSV salida | Exportación de tabla activa | utilidades/exportacion.py | tests/test_interfaz.py | Implementado y verificado |
| PNG salida | Exportación de la figura activa | interfaz/ventana_principal.py | tests/test_interfaz.py | Implementado y verificado |
| Ayuda | Teoría por método y ayuda general | interfaz/panel_ayuda.py | Revisión de contenidos y prueba de apertura | Implementado y verificado |
| A | Animación real con avance y velocidad | interfaz/ventana_principal.py | tests/test_interfaz.py | Implementado y verificado |
| B | Reporte PDF con entradas, tabla y gráfica | utilidades/reporte.py | Prueba Tk y revisión del PDF renderizado | Implementado y verificado |
| C1 | Historial y recuperación | interfaz/ventana_principal.py | tests/test_interfaz.py | Implementado y verificado |
| C2 | Tema claro y oscuro | interfaz/estilos.py | tests/test_interfaz.py | Implementado y verificado |
| D | Paquete Windows | NumLab.spec | Compilación, inicio y comparación de integración en .exe | Implementado y verificado |
| INST | Instalación de dependencias | requirements.txt | python -m pip install -r requirements.txt | Implementado y verificado |
| ARR | Arranque Python y del ejecutable | main.py, NumLab.spec | Apertura y respuesta de ventana | Implementado y verificado |
| DOC-1 | Descripción, instalación y entrega | README.md | Revisión de documentación | Implementado y verificado |
| DOC-2 | Manual de los cinco módulos | docs/manual_usuario.md | Revisión de documentación | Implementado y verificado |
| DOC-3 | Informe y resultados de casos | docs/informe.md | Contraste con pruebas numéricas | Implementado y verificado |
| DOC-4 | Guion de 18 minutos y preguntas | docs/guia_sustentacion.md | Revisión del guion | Implementado y verificado |
| DOC-5 | Plantilla de evidencias | docs/evidencias.md | Revisión de campos | Implementado y verificado |
| ENTREGA | Publicación, video, capturas de todos los casos y validación en otro equipo | docs/evidencias.md | Registro del equipo | Pendiente |
