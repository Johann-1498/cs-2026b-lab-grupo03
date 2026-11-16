"""Pruebas del generador de docstrings con proveedor grabado (Lab 09, E6)."""
import pytest
import yaml
from asistente_ia import GeneradorDocstrings, SalidaInvalida
from asistente_ia.generador_docstrings import parametros_reales
from asistente_ia.proveedor_grabado import ProveedorGrabado
from asistente_ia.puertos import PROMPTS

CASOS = {c["vars"]["id"]: c["vars"]["codigo"]
         for c in yaml.safe_load((PROMPTS / "docstrings" / "casos.yaml").read_text(encoding="utf-8"))}


def test_parametros_reales_con_kwargs_y_solo_nombre():
    assert parametros_reales(CASOS["B8"]) == ["distrito", "kg_por_material", "unidad", "opciones"]
    assert parametros_reales(CASOS["B7"]) == []


def test_acepta_docstring_valido_v3():
    doc = GeneradorDocstrings(ProveedorGrabado("docstrings", "v3")).generar("B2", CASOS["B2"])
    assert [p["nombre"] for p in doc["parametros"]][-2:] == ["latitud", "longitud"]


def test_rechaza_documentacion_que_omite_un_parametro_aunque_cumpla_el_esquema():
    # La grabación v2/B8 es JSON válido pero omite **opciones: el esquema no lo ve, el AST sí.
    with pytest.raises(SalidaInvalida, match="opciones"):
        GeneradorDocstrings(ProveedorGrabado("docstrings", "v2")).generar("B8", CASOS["B8"])


def test_rechaza_bloque_de_codigo_v2():
    with pytest.raises(SalidaInvalida):
        GeneradorDocstrings(ProveedorGrabado("docstrings", "v2")).generar("B2", CASOS["B2"])
