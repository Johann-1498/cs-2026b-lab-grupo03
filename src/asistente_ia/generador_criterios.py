"""Generador de criterios de aceptación Gherkin (Tarea A del Lab 09)."""
from __future__ import annotations

import json

from jsonschema import ValidationError, validate

from .puertos import ProveedorLLM, SalidaInvalida, cargar_esquema, cargar_plantilla
from .seguridad import neutralizar_delimitadores, verificar_salida


class GeneradorCriterios:
    def __init__(self, proveedor: ProveedorLLM, version: str = "v4") -> None:
        self._proveedor = proveedor  # Strategy: Claude, OpenAI, modelo local o grabado
        self._plantilla = cargar_plantilla("criterios", version)
        self._esquema = cargar_esquema("criterios")
        self.version = version

    def generar(self, id_historia: str, historia: str) -> dict:
        dato = neutralizar_delimitadores(historia, "historia")  # capa 1
        prompt = self._plantilla.replace("{{id}}", id_historia).replace("{{historia}}", dato)
        texto = self._proveedor.completar(prompt)
        try:
            criterios = json.loads(texto)
            validate(criterios, self._esquema)  # capa 3: contrato JSON Schema
            verificar_salida(criterios)  # capa 3: lo que el esquema no ve
        except (json.JSONDecodeError, ValidationError, SalidaInvalida) as e:
            raise SalidaInvalida(f"{self.version}/{id_historia}: {e}") from e
        return criterios  # capa 4: sigue siendo un borrador que revisa el Product Owner
