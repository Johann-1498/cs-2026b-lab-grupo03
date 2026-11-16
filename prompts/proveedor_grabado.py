"""Proveedor de promptfoo que devuelve respuestas GRABADAS (sin clave de API).

Cada respuesta se guarda tal como la dio el asistente, sin editarla, en
    prompts/<tarea>/grabaciones/<version>/<id>.txt
La versión sale de la etiqueta (label) del prompt en promptfooconfig.yaml y el
<id> de la variable `id` del caso. Para usar un modelo real basta reemplazar
este proveedor por uno de promptfoo (por ejemplo, anthropic:messages:...) con
temperature 0; las aserciones no cambian.

Uso en promptfooconfig.yaml:
    providers:
      - id: file://../proveedor_grabado.py
        label: asistente-grabado
        config: {tarea: criterios}
"""
from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def call_api(prompt: str, options: dict, context: dict) -> dict:
    config = (options or {}).get("config", {}) or {}
    tarea = config.get("tarea")
    etiqueta = (context.get("prompt") or {}).get("label", "")
    version = etiqueta.split(":")[0].strip()
    caso = str((context.get("vars") or {}).get("id", ""))
    if not tarea or not version or not caso:
        return {"error": f"Falta tarea/version/id (tarea={tarea!r}, version={version!r}, id={caso!r})"}
    ruta = RAIZ / tarea / "grabaciones" / version / f"{caso}.txt"
    if not ruta.is_file():
        return {"error": f"No existe la grabación {ruta.relative_to(RAIZ)}"}
    return {"output": ruta.read_text(encoding="utf-8")}
