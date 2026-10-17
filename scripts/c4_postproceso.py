#!/usr/bin/env python3
"""Marca como externos (System_Ext) los sistemas con la etiqueta "Externo" del workspace.dsl.

El exportador plantuml/c4plantuml de Structurizr CLI no traslada las etiquetas ($tags vacío) y
dibuja los sistemas externos igual que el sistema propio. Este paso es determinista y repetible:
 workspace.dsl  ->  structurizr export  ->  c4_postproceso.py  ->  PlantUML (PNG).
"""
import re
import sys
from pathlib import Path

C4 = Path(__file__).resolve().parent.parent / "docs" / "architecture" / "c4"
dsl = (C4 / "workspace.dsl").read_text(encoding="utf8")
externos = [
    re.sub(r"\W", "", m.group(1))
    for m in re.finditer(r'=\s*softwareSystem\s+"([^"]+)"[^\n]*"Externo', dsl)
]
if not externos:
    sys.exit("No se encontraron sistemas con la etiqueta Externo")
cambios = 0
for f in sorted((C4 / "export").glob("*.puml")):
    t = f.read_text(encoding="utf8")
    for ident in externos:
        t, n = re.subn(rf"\bSystem\(({ident}),", r"System_Ext(\1,", t)
        cambios += n
    f.write_text(t, encoding="utf8")
print(f"Sistemas externos marcados: {externos} ({cambios} reemplazos)")
