"""Módulo asistente_ia: prompts versionados detrás del puerto ProveedorLLM (Lab 09)."""
from .generador_criterios import GeneradorCriterios
from .generador_docstrings import GeneradorDocstrings
from .puertos import ProveedorLLM, SalidaInvalida

__all__ = ["GeneradorCriterios", "GeneradorDocstrings", "ProveedorLLM", "SalidaInvalida"]
