# Manual de usuario

## Inicio y navegación

Abre NumLab, elige una tarjeta y selecciona un método en la lista superior. **Comenzar** abre Raíces. **Teoría** explica la fórmula y el procedimiento del método seleccionado. **Ayuda** explica las convenciones generales. **Volver** lleva de los resultados al formulario y del formulario al inicio. **Inicio** regresa directamente al menú.

Los campos iniciales son editables. Seleccionar un ejemplo restaura los parámetros correspondientes, incluida la función o la tabla. **Limpiar** borra datos y resultados. Para recalcular, cambia las entradas y pulsa **Calcular**. Los errores de entrada aparecen en un diálogo y puedes seguir editando.

## Expresiones y tablas

Escribe con punto decimal y usa `x` en funciones escalares, `t,y` en el lado derecho de una EDO y `t` en su referencia. Se admite `^`, multiplicación explícita e implícita, paréntesis, notación científica, `sin`, `cos`, `tan`, `exp`, `ln`, `log`, `sqrt`, `abs`, `pi` y `e`. Las funciones requieren paréntesis.

En una tabla, **Añadir** abre la primera celda de la fila nueva. Haz doble clic para editar cualquier celda e Intro para confirmar. **Eliminar** borra la selección. Importa archivos UTF-8 con dos columnas separadas por coma o punto y coma. Los encabezados `x,y` son opcionales. Para datos con coma decimal, conviértelos antes a punto decimal.

## Raíces

Escribe f(x), selecciona bisección o falsa posición e introduce a y b. Para Newton escribe una semilla, y para secante escribe dos. Indica tolerancia y máximo de iteraciones. Con **Absoluto** la tolerancia usa unidades de x. Con **Relativo (%)** escribe un porcentaje. Con **Residuo** usa unidades de f(x). Una raíz conocida es opcional y habilita un error adicional. En los resultados revisa el residuo, la razón de parada y las pestañas **Función**, **Geometría** y **Convergencia**. En **Detalles** se muestra la derivada simbólica de Newton.

Activa **Comparación** para editar las cinco semillas y ejecutar los cuatro métodos. Un fallo individual aparece en su propia fila.

## Diferenciación

En **Función**, escribe f, el centro x₀ y la distancia h. En **Tabla**, utiliza cinco mediciones uniformes. NumLab ordena las abscisas e identifica la central. La tabla muestra el peso entero de cada nodo para ambas fórmulas y el resumen distingue las dos derivadas. En **Error frente a h**, la caída inicial suele indicar menor truncamiento. El aumento con h diminuto refleja la amplificación del redondeo. El modo tabla carece de una referencia analítica por defecto.

## Interpolación

Completa al menos dos puntos con abscisas únicas. Separa las consultas x* con espacios y usa decimales con punto. El resumen marca la extrapolación. Elige Lagrange para ver las bases o Newton para examinar las diferencias divididas y los polinomios parciales. **Detalles** contiene la expresión construida y la desarrollada. En comparación se cotejan ambas expresiones y sus evaluaciones.

## Integración

En **Función**, indica f, límites crecientes y n para reglas compuestas. Simpson compuesto requiere n par. En **Tabla**, el intervalo viene de los datos y n se calcula con el número de filas. Las reglas simples seleccionan extremos y, en Simpson, el punto medio medido. La opción **Minutos y Mbps** integra con el paso en segundos y muestra Mb y GB. En **Error frente a n** aparecen las curvas cuando se obtiene una referencia exacta. NumLab continúa mostrando el resultado si la referencia simbólica queda sin resolver.

## Ecuaciones diferenciales

Escribe f(t,y), t₀, y₀ y t final. Elige un tamaño h o el número N de pasos. Con h, NumLab acorta el último paso cuando es necesario y lo indica en el mensaje. Si conoces y(t), escríbela en el campo de referencia. Debe coincidir con y₀ en t₀. Las pestañas muestran soluciones, campo de pendientes y error absoluto. **Comparación** añade el refinamiento h/2 para Euler, Heun y RK4.

## Resultados, animación y archivos

Las tablas tienen desplazamiento horizontal y vertical. **Resumen** contiene resultados y errores. Las pestañas con nombres de métodos contienen los pasos. **Detalles** conserva parámetros derivados e interpretación. El número de decimales cambia la presentación. Las ausencias se muestran como «No disponible». Las escalas logarítmicas omiten los valores iguales a cero.

**Siguiente**, **Anterior**, **Reproducir** y **Pausar** recorren registros calculados. El control de velocidad cambia la cadencia. La barra de cada figura permite mover, hacer zoom, restaurar y guardar. **CSV** exporta la tabla activa con precisión completa. **PNG** exporta la figura activa. **PDF** reúne entradas, resumen, figura visible y tablas. Cada botón abre un diálogo para elegir la ruta.

**Historial** recupera cálculos de la sesión mediante doble clic o **Recuperar cálculo**. **Tema oscuro** cambia la paleta y conserva los datos de trabajo.
