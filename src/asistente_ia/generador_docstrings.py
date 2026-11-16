"""Generador de docstrings (Tarea B del Lab 09) con verificación de la firma por AST."""
from __future__ import annotations

import ast
import json
import textwrap

from jsonschema import ValidationError, validate

from .puertos import ProveedorLLM, SalidaInvalida, cargar_esquema, cargar_plantilla
from .seguridad import neutralizar_delimitadores, verificar_salida


def parametros_reales(codigo: str) -> list[str]:
    """Parámetros de la firma (sin self/cls), calculados con ast: la fuente de verdad."""
    funcion = next(
        (n for n in ast.walk(ast.parse(textwrap.dedent(codigo))) if isinstance(n, ast.FunctionDef)), None
    )
    if funcion is None:
        raise SalidaInvalida("El código no contiene una función")
    a = funcion.args
    nombres = [p.arg for p in a.posonlyargs + a.args + a.kwonlyargs]
    nombres += [x.arg for x in (a.vararg, a.kwarg) if x is not None]
    return [n for n in nombres if n not in ("self", "cls")]


class GeneradorDocstrings:
    def __init__(self, proveedor: ProveedorLLM, version: str = "v3") -> None:
        self._proveedor = proveedor
        self._plantilla = cargar_plantilla("docstrings", version)
        self._esquema = cargar_esquema("docstrings")
        self.version = version

    def generar(self, id_funcion: str, codigo: str) -> dict:
        dato = neutralizar_delimitadores(codigo, "codigo")
        prompt = self._plantilla.replace("{{id}}", id_funcion).replace("{{codigo}}", dato)
        texto = self._proveedor.completar(prompt)
        try:
            doc = json.loads(texto)
            validate(doc, self._esquema)
            verificar_salida(doc)
            documentados = [p["nombre"].lstrip("*") for p in doc["parametros"]]
            reales = parametros_reales(codigo)
            if sorted(documentados) != sorted(reales):
                raise SalidaInvalida(f"Parámetros documentados {documentados} != reales {reales}")
        except (json.JSONDecodeError, ValidationError, SalidaInvalida) as e:
            raise SalidaInvalida(f"{self.version}/{id_funcion}: {e}") from e
        return doc
