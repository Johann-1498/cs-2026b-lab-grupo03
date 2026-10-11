#!/usr/bin/env python3
"""Verificador automático de las reglas C1-C5 (Tabla 2 de la guía del Laboratorio 05).

Uso:  python scripts/verificar_consistencia.py
Lee docs/design/*.puml|*.mmd y src/. Devuelve código 1 si alguna regla falla.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DISEÑO = RAIZ / "docs" / "design"
SRC = RAIZ / "src"


def snake(nombre: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", nombre).lower()


# ---------------------------------------------------------------- clases.puml
def leer_clases() -> dict[str, dict]:
    clases: dict[str, dict] = {}
    actual = None
    for linea in (DISEÑO / "clases.puml").read_text(encoding="utf8").splitlines():
        m = re.match(r"\s*(class|interface|enum)\s+(\w+)", linea)
        if m and linea.rstrip().endswith("{") or (m and "{" not in linea):
            actual = m.group(2)
            clases[actual] = {"tipo": m.group(1), "ops": set(), "attrs": set(), "valores": []}
            if "{" not in linea:
                actual = None
            continue
        if actual is None:
            continue
        if linea.strip() == "}":
            actual = None
            continue
        op = re.match(r"\s*[+\-#~]\s*(\w+)\(", linea)
        if op:
            clases[actual]["ops"].add(op.group(1))
            continue
        at = re.match(r"\s*[+\-#~]\s*(\w+):", linea)
        if at:
            clases[actual]["attrs"].add(at.group(1))
            continue
        if clases[actual]["tipo"] == "enum" and linea.strip():
            clases[actual]["valores"].append(linea.strip())
    return clases


def realizaciones(texto: str) -> dict[str, str]:
    """hija -> interfaz (A <|.. B)."""
    return {b: a for a, b in re.findall(r"(\w+)\s*<\|\.\.\s*(\w+)", texto)}


def operaciones_de(clase: str, clases: dict, texto: str) -> set[str]:
    ops = set(clases[clase]["ops"])
    real = realizaciones(texto)
    if clase in real:  # una clase que realiza una interfaz hereda sus operaciones
        ops |= clases[real[clase]]["ops"]
    return ops


# ---------------------------------------------------------------- reglas
def c1(clases: dict) -> list[str]:
    errores = []
    texto = (DISEÑO / "clases.puml").read_text(encoding="utf8")
    seq = (DISEÑO / "secuencia-solicitar-recojo.puml").read_text(encoding="utf8")
    alias = dict(re.findall(r'participant\s+"([^"\\]+)(?:\\n[^"]*)?"\s+as\s+(\w+)', seq))
    alias = {v: k for k, v in alias.items()}
    ignorar = {"UI", "C"}  # PWA y controlador: capa de presentación, fuera del diagrama de dominio
    for l in seq.splitlines():
        m = re.match(r"\s*(\w+)\s+-+>>?\s+(\w+)\s*:\s*(\w+)\(", l)
        if not m:
            continue
        _, dest, op = m.groups()
        if dest in ignorar:
            continue
        clase = alias.get(dest)
        if clase not in clases:
            errores.append(f"C1: la línea de vida {dest} ({clase}) no es una clase del diagrama")
        elif op not in operaciones_de(clase, clases, texto):
            errores.append(f"C1: {clase}.{op}() no existe en el diagrama de clases")
    return errores


def c2(clases: dict) -> list[str]:
    errores = []
    mmd = (DISEÑO / "estados-solicitud.mmd").read_text(encoding="utf8")
    permitidas = set(clases["Solicitud"]["ops"]) | set(clases["ServicioSolicitudes"]["ops"])
    estados = set(clases["EstadoSolicitud"]["valores"])
    usados = set()
    for a, b, ev in re.findall(r"^\s*(\S+)\s+-->\s+(\S+)\s*:\s*(\w+)\(", mmd, re.M):
        if ev not in permitidas:
            errores.append(f"C2: la transición {a}->{b} usa {ev}(), que no es operación de la clase")
        usados |= {a, b} - {"[*]"}
    if usados != estados:
        errores.append(f"C2: estados del .mmd {sorted(usados)} != enum {sorted(estados)}")
    return errores


def c3() -> list[str]:
    t = (DISEÑO / "clases.puml").read_text(encoding="utf8")
    errores = []
    if not re.search(r'Solicitud\s+"1"\s+\*--\s+"1\.\.\*"\s+ItemMaterial', t):
        errores.append("C3: Solicitud debe componer 1..* ItemMaterial")
    for l in t.splitlines():
        if re.match(r"\s*\w+\s+(--|\*--|o--|-->)\s+\w+", l):
            errores.append(f"C3: asociación sin multiplicidad: {l.strip()}")
    return errores


def c4() -> list[str]:
    t = (DISEÑO / "paquetes.puml").read_text(encoding="utf8")
    aristas = re.findall(r"\b([A-Z]{3})\s+\.\.>\s+([A-Z]{3})", t)
    grafo: dict[str, set[str]] = {}
    for a, b in aristas:
        grafo.setdefault(a, set()).add(b)
    errores, estado = [], {}

    def dfs(n, ruta):
        estado[n] = 1
        for v in grafo.get(n, ()):
            if estado.get(v) == 1:
                errores.append("C4: ciclo " + " -> ".join(ruta + [n, v]))
            elif v not in estado:
                dfs(v, ruta + [n])
        estado[n] = 2

    for n in list(grafo):
        if n not in estado:
            dfs(n, [])
    return errores


def c5(clases: dict) -> list[str]:
    errores = []
    tree = {}
    for py in SRC.rglob("*.py"):
        for n in ast.walk(ast.parse(py.read_text(encoding="utf8"))):
            if isinstance(n, ast.ClassDef):
                tree[n.name] = {f.name for f in n.body if isinstance(f, ast.FunctionDef)}
    for nombre, info in clases.items():
        if info["tipo"] == "enum" or nombre == "Pesaje":
            continue
        if nombre not in tree:
            errores.append(f"C5: la clase {nombre} no existe en el código")
            continue
        faltan = {snake(o) for o in info["ops"]} - tree[nombre]
        # operaciones heredadas de una interfaz (realización) o privadas con prefijo _
        faltan = {o for o in faltan if o not in tree.get(realizaciones(
            (DISEÑO / "clases.puml").read_text(encoding="utf8")).get(nombre, ""), set())}
        faltan = {o for o in faltan if "_" + o not in tree[nombre]}
        if faltan:
            errores.append(f"C5: {nombre} no implementa {sorted(faltan)}")
    return errores


def main() -> int:
    clases = leer_clases()
    resultados = {"C1": c1(clases), "C2": c2(clases), "C3": c3(), "C4": c4(), "C5": c5(clases)}
    fallo = False
    for regla, errs in resultados.items():
        print(f"{regla}: {'OK' if not errs else 'FALLA'}")
        for e in errs:
            fallo = True
            print("   -", e)
    print(f"\n{len(clases)} clases/interfaces/enums leídas de clases.puml")
    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main())
