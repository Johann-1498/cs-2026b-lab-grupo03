"""Puerto hacia el LLM (patrón Strategy, ADR-001): el dominio no conoce al proveedor."""
from __future__ import annotations

import json
import pathlib
from abc import ABC, abstractmethod

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PROMPTS = RAIZ / "prompts"


class SalidaInvalida(Exception):
    """La respuesta del LLM no cumple el contrato: se descarta y se registra."""


class ProveedorLLM(ABC):
    """Puerto: recibe un prompt y devuelve el texto del modelo. Claude, OpenAI, local o grabado."""

    @abstractmethod
    def completar(self, prompt: str) -> str: ...


def cargar_plantilla(tarea: str, version: str) -> str:
    return (PROMPTS / tarea / f"{version}.txt").read_text(encoding="utf-8")


def cargar_esquema(tarea: str) -> dict:
    return json.loads((PROMPTS / tarea / "esquema.json").read_text(encoding="utf-8"))
