"""Capas 1 y 3 de la defensa frente a la inyección de prompts (Figura 4 de la guía)."""
from __future__ import annotations

import re

from .puertos import SalidaInvalida

# Fragmentos que solo existen en nuestras plantillas: si salen en la respuesta, el prompt se filtró.
MARCAS_DEL_PROMPT = ("# ROL", "# CONTEXTO", "# TAREA", "# RESTRICCIONES", "# FORMATO DE SALIDA")


def neutralizar_delimitadores(texto: str, etiqueta: str) -> str:
    """Capa 1: el dato no puede abrir ni cerrar el delimitador (<historia>, <codigo>)."""
    return re.sub(rf"<\s*/?\s*{etiqueta}\b[^>]*>", "[etiqueta eliminada]", texto, flags=re.IGNORECASE)


def verificar_salida(contenido: object) -> None:
    """Capa 3 (complemento del JSON Schema): rechaza salidas que el esquema no puede detectar."""
    import json

    plano = json.dumps(contenido, ensure_ascii=False)
    for marca in MARCAS_DEL_PROMPT:
        if marca in plano:
            raise SalidaInvalida(f"La salida filtra el prompt ({marca})")
    if re.fullmatch(r"\W*aprobado\W*", plano, flags=re.IGNORECASE):
        raise SalidaInvalida("La salida obedeció una inyección (APROBADO)")
