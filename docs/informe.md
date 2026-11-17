# Informe técnico · NumLab

**Programa** Ingeniería de Software · Métodos Numéricos · 2026-2  
**Institución** Corporación Universitaria Empresarial Alexander von Humboldt

## Problema y objetivos

Los problemas de rendimiento, estimación de tasas, reconstrucción de datos, acumulación y evolución temporal suelen requerir aproximaciones. NumLab convierte los métodos del curso en procedimientos observables: cada cálculo conserva sus operaciones intermedias, presenta sus supuestos y permite estudiar la sensibilidad a los parámetros. El objetivo de verificación es reproducir la sección 11 y someter los algoritmos a entradas distintas y condiciones de frontera.

## Arquitectura

`main.py` crea la aplicación Tk. Los formularios entregan valores al coordinador de cálculo en `utilidades/comparaciones.py`. El coordinador interpreta las expresiones con una gramática cerrada, selecciona métodos y organiza el resumen. Los módulos del núcleo devuelven `Resultado` con valor, estado, mensaje, tabla y datos auxiliares. Las gráficas reciben el cálculo ya construido. El cálculo se ejecuta fuera del hilo de Tkinter y la referencia simbólica de integración tiene un presupuesto de cuatro segundos por expresión e intervalo.

El parser crea nodos SymPy a partir de tokens autorizados y evalúa el árbol con operaciones matemáticas explícitas. Las funciones de una variable reciben x y las EDO reciben t, y. Las mallas y los límites se verifican antes de usarse. Las operaciones subyacentes usan punto flotante, excepto la construcción racional de interpolantes a partir de la representación decimal de los nodos.

Se admiten hasta 25 nodos para interpolación simbólica y hasta 10 000 iteraciones, pasos o subintervalos. Las tablas de entrada uniformes usan una tolerancia relativa de 10⁻⁶. Los límites de integración deben ser crecientes. Las gráficas de mallas grandes pueden muestrear la geometría, mientras se conserva la tabla completa. Los errores absolutos miden magnitud de la diferencia y los relativos dividen por la magnitud de la referencia y multiplican por cien. El porcentaje queda indefinido si la referencia vale cero.

## Raíces

Bisección divide el intervalo con c=(a+b)/2. Falsa posición usa el corte de la secante c=(a·f(b)−b·f(a))/(f(b)−f(a)) y actualiza el extremo que tiene el signo de f(c). Ambos métodos requieren continuidad y cambio de signo, admitiendo una raíz inicial exacta. Newton corta la tangente en x−f(x)/f′(x), mientras secante estima esa pendiente con las dos últimas iteraciones. Newton puede converger cuadráticamente cerca de una raíz simple, y secante evita el cálculo de derivadas. Falsa posición puede conservar el mismo extremo durante muchas iteraciones.

| Caso | Bisección | Falsa posición | Newton | Secante |
|---|---:|---:|---:|---:|
| R-1 | 2.09455204 · 20 | 2.09455126 · 13 | 2.09455148 · 5 | 2.09455148 · 6 |
| R-2 | 0.56714344 · 20 | 0.56714338 · 7 | 0.56714329 · 3 | 0.56714329 · 5 |
| R-3 | 6 exacto · 1 | 6.00000014 · 13 | 6 exacto · 5 | 6.00000000 · 6 |

Se usó tolerancia absoluta de 10⁻⁶ sobre el cambio de aproximación, con detección de cero exacto. Por ello el redondeo a seis decimales de bisección en R-1 puede diferir en el último dígito de la raíz redondeada. En R-4a se rechaza el intervalo. En R-4b Newton detecta el ciclo 0→1→0, en R-4c se detiene por derivada nula y en R-4d llega a −1.76929235 con semilla −2. Un cambio pequeño, un residuo pequeño y una distancia pequeña a la raíz son medidas distintas.

## Diferenciación

Se usan los pesos [1,−8,0,8,−1]/(12h) y [−1,16,−30,16,−1]/(12h²). La expansión de Taylor alrededor del centro cancela los términos de error anteriores a h⁴. En D-1 la referencia es −0.7211012741 y −2.8098653506.

| Caso | h | Primera | Segunda |
|---|---:|---:|---:|
| D-1 | 0.5 | −0.7206978935 | −2.8097181764 |
| D-1 | 0.1 | −0.7211006241 | −2.8098651139 |
| D-1 | 0.01 | −0.7211012740 | −2.8098653504 |
| D-2 | 0.5 | 58 | 6 |
| D-3 | 0.1 | 3.7560993 | 2.9374009 |

En D-1 el error de la primera derivada cae cerca de 621 veces al dividir h por cinco, frente a 625 según el término dominante. Para la segunda fórmula, la cancelación y la división por h² explican que el resultado D-1 con h=0.01 difiera de la última cifra de la guía en unos 3×10⁻¹⁰. Las pruebas conservan el número publicado y una tolerancia de 5×10⁻¹⁰. Para D-3 las referencias son 3.7560492271 y 2.9373878798. Los errores son aproximadamente 5.01×10⁻⁵ y 1.30×10⁻⁵. En D-2 solo se suministran muestras. El resultado tabulado identifica el centro y los pesos aplicados.

## Interpolación

Lagrange suma yᵢLᵢ(x), con Lᵢ(x)=∏ⱼ≠ᵢ(x−xⱼ)/(xᵢ−xⱼ). Newton calcula Dᵢ,ₖ=(Dᵢ₊₁,ₖ₋₁−Dᵢ,ₖ₋₁)/(xᵢ₊ₖ−xᵢ) y emplea D₀,ₖ como coeficientes de productos sucesivos. Los polinomios expandidos coinciden exactamente en ambos casos y las evaluaciones se cotejan numéricamente. La unicidad se deduce porque un polinomio de grado máximo n con n+1 raíces distintas ha de ser cero.

| Caso | Coeficientes de Newton | Evaluación |
|---|---|---:|
| I-1 | 120, 90, −20/3, 5/84 | P(6)=439.047619 |
| I-2 | 42, 26, 0, 11/5, −46/105 | P(2.5)=97.628571 |

En I-2 el polinomio expandido es −46x⁴/105 + 106x³/21 − 83x²/6 + 1627x/42 + 892/35. Los datos ruidosos y la extrapolación pueden hacer que el polinomio sea inadecuado para predecir nuevas mediciones.

## Integración

Trapecio aplica h/2 a los pesos 1,2,…,2,1. Simpson aplica h/3 a los pesos 1,4,2,…,4,1 y utiliza pares de subintervalos. Las versiones simples tienen uno y dos subintervalos respectivamente. La aproximación lineal tiene error global O(h²) bajo suavidad suficiente y Simpson tiene error O(h⁴). Si se cancelan los términos dominantes, la caída observada puede ser mayor, como se aprecia en N-1. Una malla muestra valores puntuales y no garantiza que una función tenga integral ordinaria si hay singularidades entre nodos.

| Regla | n | N-1 | N-2 (kWh) |
|---|---:|---:|---:|
| Trapecio simple | 1 | 0.750000000 | 2116.118980 |
| Simpson simple | 2 | 0.783333333 | 2295.725388 |
| Trapecio compuesto | 4 | 0.782794118 | 2292.565221 |
| Simpson compuesto | 4 | 0.785392157 | 2306.479033 |
| Trapecio compuesto | 8 | — | 2303.617530 |
| Simpson compuesto | 8 | — | 2307.301634 |
| Trapecio compuesto | 10 | 0.784981497 | — |
| Simpson compuesto | 10 | 0.785398153 | — |
| Valor exacto | — | π/4 | 2307.359537 |

N-3 usa h=600 s. Trapecio compuesto da 825000 Mb (103.125 GB) y Simpson compuesto 830000 Mb (103.75 GB). Las mediciones permiten comparar estimaciones, pero la transferencia exacta requeriría conocer la tasa entre muestras.

## Ecuaciones diferenciales

Euler avanza con y siguiente=y+h·f(t,y). Heun predice con Euler y corrige al promediar pendientes inicial y final predicha. RK4 usa cuatro pendientes con pesos 1,2,2,1 sobre seis, en inicio, medio, medio y final. Los órdenes globales son uno, dos y cuatro para soluciones suaves en una región de estabilidad. El paso se mantiene hasta el último tramo, que se reduce si hiciera falta.

| Caso | Euler | Heun | RK4 | Referencia |
|---|---:|---:|---:|---:|
| E-1 en t=5 | 679.0270 | 733.4076 | 741.8001 | 741.8413 |
| E-2 en t=2 | 4.865785 | 5.233055 | 5.305363 | 5.305472 |

En E-1 los errores finales son 62.8144, 8.4337 y 0.0412 respectivamente. El análisis h/2 permite contrastar el costo extra con la reducción del error y estimar el orden observado mediante log₂(E(h)/E(h/2)). Si solo se conoce la malla refinada, el cambio es una métrica de sensibilidad.

## Verificación y conclusiones

Las pruebas cubren fórmulas, ejemplos, estados de fallo, parser, CSV, equivalencia algebraica y flujos de Tkinter. Los casos conocidos permiten distinguir el error de truncamiento de un fallo de implementación. Las visualizaciones muestran qué hipótesis sustentan cada método y por qué un refinamiento puede ayudar en un rango de discretización y amplificar el redondeo en otro.

## Bibliografía

- Molina Díaz, Oscar Emilio. *NumLab: laboratorio interactivo de métodos numéricos en Python*. Guía institucional del proyecto final de Métodos Numéricos, 2026-2, secciones 5–13.
- Burden, Richard L. y J. Douglas Faires. *Análisis numérico*. Cengage Learning. Capítulos de raíces, interpolación, diferenciación, cuadratura y problemas de valor inicial.
