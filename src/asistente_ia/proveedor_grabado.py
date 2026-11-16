"""Adaptador de prueba: devuelve las respuestas grabadas en prompts/<tarea>/grabaciones/."""
from __future__ import annotations

import re

from .puertos import PROMPTS, ProveedorLLM


class ProveedorGrabado(ProveedorLLM):
    def __init__(self, tarea: str, version: str) -> None:
        self._base = PROMPTS / tarea / "grabaciones" / version

    def completar(self, prompt: str) -> str:
        # El dato real va al final del prompt (después del ejemplo): se toma la ÚLTIMA coincidencia.
        ids = re.findall(r'<(?:historia|codigo) id="([^"]+)"', prompt) or re.findall(r"\((\w+)\):", prompt)
        if not ids:
            raise KeyError("El prompt no identifica el caso (id)")
        return (self._base / f"{ids[-1]}.txt").read_text(encoding="utf-8")
