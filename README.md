# NumLab · Laboratorio Interactivo de Métodos Numéricos

Aplicación de escritorio para explorar raíces, diferenciación, interpolación, integración y ecuaciones diferenciales ordinarias. Proyecto final de Métodos Numéricos de Ingeniería de Software, Corporación Universitaria Empresarial Alexander von Humboldt, periodo 2026-2.

## Objetivos

- Implementar las fórmulas del curso y exponer las operaciones que conducen a cada resultado.
- Comparar convergencia, errores, geometría y sensibilidad a los parámetros.
- Reproducir los casos de la guía y aceptar funciones y tablas nuevas.

## Instalación y ejecución en IntelliJ IDEA

Abre esta carpeta como proyecto. Selecciona un intérprete Python 3.10 o posterior con Tkinter. Abre la terminal de IntelliJ en la carpeta que contiene `main.py` y ejecuta:

```powershell
python -m pip install -r requirements.txt
python main.py
```

En IntelliJ también puedes crear una configuración **Python** con `main.py` como script, la raíz del proyecto como directorio de trabajo y el mismo intérprete utilizado para instalar las dependencias. Si prefieres aislar las dependencias en Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Primer recorrido

1. Abre **Cálculo de raíces** y selecciona **R-3 · Ley de Amdahl**.
2. Pulsa **Calcular**. Bisección obtiene exactamente 6 en la primera fila.
3. Activa **Comparación** y vuelve a calcular. Revisa **Resumen**, las tablas por método y la pestaña **Convergencia**.
4. Desde **Inicio** abre otro módulo. El selector **Ejemplo oficial** incluye todas las variantes de la sección 11.

Usa CSV para exportar la tabla seleccionada, PNG para la gráfica abierta y PDF para el reporte del cálculo. **Historial** recupera entradas y resultados durante la sesión.

## Tecnologías y estructura

- Python y Tkinter/ttk para la interfaz.
- NumPy para muestreo y mallas de visualización. SymPy para expresiones, derivadas exactas, polinomios y referencias de integración.
- Matplotlib para figuras incrustadas. CSV de la biblioteca estándar y ReportLab para reportes.
- pytest y Git para verificación y control de versiones.

| Carpeta | Responsabilidad |
|---|---|
| `nucleo/` | Algoritmos y contrato `Resultado` |
| `utilidades/` | Parser, validación, casos, comparación y salida |
| `interfaz/` | Ventanas, formularios, navegación e historial |
| `graficas/` | Figuras reutilizables sin dependencia de Tk |
| `tests/` | Pruebas numéricas, validaciones e integración Tk |
| `docs/` | Manual, informe, sustentación y trazabilidad |
| `ejemplos/` | CSV para practicar la importación |

```powershell
python -m pytest -v
```

Las pruebas gráficas necesitan una sesión de escritorio. Para construir el ejecutable de Windows en la plataforma de destino:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm NumLab.spec
.\dist\NumLab\NumLab.exe
```

Distribuye toda la carpeta `dist/NumLab`, incluidos sus archivos de soporte.

## Entrega del equipo

- Integrante 1 y código institucional: pendiente de diligenciar.
- Integrante 2 y código institucional: pendiente de diligenciar.
- Repositorio y video: pendientes de registrar en [Evidencias](docs/evidencias.md).

Cada integrante debe registrar sus contribuciones con su identidad Git, publicar el repositorio autorizado y comprobar el acceso del docente. Después de grabar la demostración, añade su enlace y las capturas de los casos a la plantilla. Consulta el [manual](docs/manual_usuario.md), el [informe](docs/informe.md), la [guía de sustentación](docs/guia_sustentacion.md) y la [matriz](docs/checklist_requisitos.md).
