import pytest

from nucleo.resultado import Resultado
from utilidades.errores import errores
from utilidades.exportacion import guardar_csv, leer_csv
from utilidades.validaciones import nodos, real


@pytest.mark.parametrize("valor", ["nan", "inf", "-inf", "número", None])
def test_real_invalido(valor):
    with pytest.raises(ValueError):
        real(valor, "Dato")


def test_contrato_y_errores():
    r, s = Resultado(1.0, True, "Correcto"), Resultado(None, False, "Detenido")
    r.tabla.append({"i": 1})
    assert not s.tabla
    assert errores(9, 10) == {"Error absoluto": 1, "Error relativo (%)": 10}
    assert errores(1, 0)["Error relativo (%)"] is None


def test_csv(tmp_path):
    ruta = tmp_path / "datos.csv"
    guardar_csv(ruta, [{"x": 0, "y": 1}, {"x": 1, "y": 2}])
    assert leer_csv(ruta) == [(0, 1), (1, 2)]
    ruta.write_text("\n  \nx;y\n0;1\n2;3", encoding="utf-8")
    assert leer_csv(ruta) == [(0, 1), (2, 3)]


def test_tabla_debe_ser_iterable():
    with pytest.raises(ValueError, match="tabla con dos columnas"):
        nodos(None)


@pytest.mark.parametrize("contenido", ["", "x,y", "x,y\n0,1,2", 'x,y\n"0,1', "x,y\n0,nan\n1,3"])
def test_csv_invalido(tmp_path, contenido):
    ruta = tmp_path / "datos.csv"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(ValueError):
        leer_csv(ruta)
