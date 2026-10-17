#!/usr/bin/env python3
"""Verificador del modelo C4 (Laboratorio 06): lista de revisión + coherencia con Lab 04 y Lab 05.

Uso:  python scripts/verificar_c4.py        (código de salida 1 si algo falla)
Lee docs/architecture/c4/workspace.dsl y docs/design/paquetes.puml.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DSL = RAIZ / "docs" / "architecture" / "c4" / "workspace.dsl"
PAQUETES = RAIZ / "docs" / "design" / "paquetes.puml"

# Tecnologías ausentes de los ADR / despliegue.py (error típico de la IA, guía 1.7)
PROHIBIDAS = ["kafka", "kubernetes", "rabbitmq", "mongodb", "microservic", "docker", "graphql", "keycloak"]
NOMBRES_PROHIBIDOS = {"docker", "servidor", "nube", "vps", "server", "cloud"}


def cadenas(resto: str) -> list[str]:
    return re.findall(r'"([^"]*)"', resto)


def parsear():
    elementos: dict[str, dict] = {}
    relaciones: list[dict] = []
    vistas: list[dict] = []
    despliegue = {"profundidad": 0, "instancias": set(), "nodos": []}
    pila: list[str | None] = []
    modo = None  # None | 'deploy' | 'dynamic' | 'views'
    prof_nodos = 0
    pila_nodo: list[bool] = []
    for bruta in DSL.read_text(encoding="utf8").splitlines():
        l = bruta.split("#")[0].strip() if not bruta.strip().startswith('"') else bruta.strip()
        if not l:
            continue
        m = re.match(r"^(\w+)\s*=\s*(person|softwareSystem|container|component)\s+(.*)$", l)
        if m:
            ident, tipo, resto = m.groups()
            cs = cadenas(resto)
            ruta = ".".join([p for p in pila if p] + [ident])
            elementos[ruta] = {
                "tipo": tipo, "nombre": cs[0] if cs else "", "desc": cs[1] if len(cs) > 1 else "",
                "tec": cs[2] if len(cs) > 2 and tipo in ("container", "component") else "",
                "tags": (cs[2] if tipo in ("softwareSystem",) and len(cs) > 2 else (cs[3] if len(cs) > 3 else "")),
            }
            pila.append(ident) if l.endswith("{") else None
            continue
        if re.match(r"^\w+\s*=\s*deploymentEnvironment", l):
            modo = "deploy"; pila.append(None); pila_nodo.append(False); continue
        if modo == "deploy":
            if re.match(r"^(\w+\s*=\s*)?deploymentNode", l):
                prof_nodos += 1
                despliegue["profundidad"] = max(despliegue["profundidad"], prof_nodos)
                cs = cadenas(l)
                despliegue["nodos"].append((cs[0], cs[2] if len(cs) > 2 else ""))
                pila_nodo.append(True); pila.append(None)
                continue
            mi = re.match(r"^\w+\s*=\s*containerInstance\s+([\w.]+)", l)
            if mi:
                despliegue["instancias"].add(mi.group(1)); continue
            if l.endswith("{"):
                pila.append(None); pila_nodo.append(False); continue
            if l == "}":
                pila.pop()
                if pila_nodo and pila_nodo.pop():
                    prof_nodos -= 1
                else:
                    modo = None if not pila_nodo else "deploy"
                continue
            continue
        mv = re.match(r"^(systemContext|container|component|dynamic|deployment)\s+(.*)\{$", l)
        if mv:
            tipo = mv.group(1); cs = cadenas(mv.group(2))
            vistas.append({"tipo": tipo, "clave": cs[0] if cs else "", "desc": cs[1] if len(cs) > 1 else "", "pasos": []})
            if tipo == "dynamic":
                modo = "dynamic"
            pila.append(None); continue
        if modo == "dynamic":
            mr = re.match(r"^([\w.]+)\s*->\s*([\w.]+)\s*(.*)$", l)
            if mr:
                vistas[-1]["pasos"].append((mr.group(1), mr.group(2)))
                continue
        mr = re.match(r"^([\w.]+)\s*->\s*([\w.]+)\s*(.*)$", l)
        if mr and modo is None:
            cs = cadenas(mr.group(3))
            relaciones.append({"o": mr.group(1), "d": mr.group(2), "desc": cs[0] if cs else "", "tec": cs[1] if len(cs) > 1 else ""})
            continue
        if l.endswith("{"):
            pila.append(None)
        elif l == "}":
            if pila:
                pila.pop()
            if modo == "dynamic":
                modo = None
    return elementos, relaciones, vistas, despliegue


def paquetes():
    t = PAQUETES.read_text(encoding="utf8")
    alias = {a: n for n, a in re.findall(r'package\s+"(\w+)"\s+as\s+(\w+)', t)}
    aristas = [(alias[a], alias[b], et) for a, b, et in re.findall(r"\b([A-Z]{3})\s+\.\.>\s+([A-Z]{3})\s*:?\s*([^\n]*)", t)]
    return set(alias.values()), aristas


def hay_ciclo(aristas: list[tuple[str, str]]) -> list[str] | None:
    grafo: dict[str, set[str]] = {}
    for a, b in aristas:
        grafo.setdefault(a, set()).add(b)
    estado: dict[str, int] = {}

    def dfs(n, ruta):
        estado[n] = 1
        for v in grafo.get(n, ()):
            if estado.get(v) == 1:
                return ruta + [n, v]
            if v not in estado:
                r = dfs(v, ruta + [n])
                if r:
                    return r
        estado[n] = 2
        return None

    for n in list(grafo):
        if n not in estado:
            r = dfs(n, [])
            if r:
                return r
    return None


def main() -> int:
    el, rel, vistas, desp = parsear()
    res: dict[str, list[str]] = {}
    tipo = lambda r: el[r]["tipo"] if r in el else "?"
    ext = {r for r, e in el.items() if "Externo" in e["tags"]}

    # E1 contexto -----------------------------------------------------------
    e = []
    personas = [r for r in el if tipo(r) == "person"]
    if len(personas) < 2: e.append(f"Se requieren ≥ 2 personas (hay {len(personas)})")
    if len(ext) < 2: e.append(f"Se requieren ≥ 2 sistemas externos con etiqueta Externo (hay {len(ext)})")
    ctx = [v for v in vistas if v["tipo"] == "systemContext"]
    if not ctx: e.append("Falta la vista systemContext")
    res["E1 contexto"] = e

    # General + elementos + relaciones (lista de revisión, Tabla 3) -------------
    e = []
    for v in vistas:
        if not v["clave"] or not v["desc"]:
            e.append(f"Vista {v['clave'] or v['tipo']}: falta título o descripción")
    for r, x in el.items():
        if not x["nombre"] or not x["desc"]:
            e.append(f"{r}: falta nombre o descripción")
        if x["tipo"] in ("container", "component") and not x["tec"]:
            e.append(f"{r}: falta tecnología")
    for x in rel:
        if not x["desc"]:
            e.append(f"Relación {x['o']} -> {x['d']} sin etiqueta")
        entre_comp = tipo(x["o"]) == "component" and tipo(x["d"]) == "component"
        persona_sist = tipo(x["o"]) == "person" and tipo(x["d"]) in ("softwareSystem",)
        sist_ext = tipo(x["o"]) == "softwareSystem" and tipo(x["d"]) == "softwareSystem"
        if not (entre_comp or persona_sist or sist_ext or tipo(x["o"]) == "person" and False) and not x["tec"] and tipo(x["o"]) != "person":
            e.append(f"Relación {x['o']} -> {x['d']} sin protocolo")
        if tipo(x["o"]) == "person" and tipo(x["d"]) == "container" and not x["tec"]:
            e.append(f"Relación {x['o']} -> {x['d']} sin protocolo")
        if re.match(r"^(usa|uses|llama a)$", x["desc"].strip().lower()) and tipo(x["o"]) == "person":
            e.append(f"Relación {x['o']} -> {x['d']}: etiqueta vaga '{x['desc']}'")
    res["Lista de revisión (general, elementos, relaciones)"] = e

    # E2 contenedores -----------------------------------------------------------
    e = []
    cont = [r for r in el if tipo(r) == "container"]
    if len(cont) < 3: e.append(f"Se requieren ≥ 3 contenedores (hay {len(cont)})")
    for r in cont:
        if el[r]["nombre"].strip().lower() in NOMBRES_PROHIBIDOS:
            e.append(f"Contenedor con nombre prohibido: {el[r]['nombre']}")
    texto = DSL.read_text(encoding="utf8").lower()
    model = texto[: texto.index("views {")]
    modelo_sin_comentarios = "\n".join(l for l in model.splitlines() if not l.strip().startswith("#"))
    for p in PROHIBIDAS:
        if p in modelo_sin_comentarios:
            e.append(f"Tecnología no incluida en el ADR-001/despliegue.py: '{p}'")
    tec = " ".join(el[r]["tec"].lower() for r in cont)
    for req in ("django", "postgresql", "redis", "celery"):
        if req not in tec:
            e.append(f"Falta el contenedor con tecnología {req} (ADR-001/despliegue.py)")
    res["E2 contenedores (coherencia con ADR-001)"] = e

    # E3 componentes ------------------------------------------------------------
    e = []
    comps = {r.split(".")[-1]: r for r in el if tipo(r) == "component"}
    nombres_pkg, aristas_pkg = paquetes()
    if set(comps) != nombres_pkg:
        e.append(f"Componentes {sorted(comps)} != paquetes del Lab 05 {sorted(nombres_pkg)}")
    if len(comps) < 4: e.append("Se requieren ≥ 4 componentes")
    aristas_c4 = [(x["o"].split(".")[-1], x["d"].split(".")[-1], x["desc"]) for x in rel
                  if tipo(x["o"]) == "component" and tipo(x["d"]) == "component"]
    # aristas hacia/desde infraestructura (componente) también cuentan
    c = hay_ciclo([(a, b) for a, b, _ in aristas_c4] + [(x["o"].split(".")[-1], x["d"].split(".")[-1]) for x in rel
                                                         if tipo(x["o"]) == "component" and tipo(x["d"]) == "component"])
    if c: e.append("Ciclo entre componentes: " + " -> ".join(c))
    # Correspondencia C4 (uso en ejecución) <-> UML (dependencia de compilación), ADR-004:
    #  - A -> B directa                      => dependencia A -> B
    #  - A -> B "(puerto ...)" inversa        => dependencia B -> A (el puerto lo define el receptor)
    #  - A -> infraestructura "(puerto ...)"  => dependencia A -> solicitudes (dueño de los puertos)
    pkg = {(a, b) for a, b, _ in aristas_pkg}
    cubiertas: set[tuple[str, str]] = set()
    for a, b, d in aristas_c4:
        cand = {(a, b)}
        if "puerto" in d.lower():
            cand |= {(b, a)}
            if b == "infraestructura":
                cand.add((a, "solicitudes"))
        if cand & pkg:
            cubiertas |= cand & pkg
        else:
            e.append(f"Dependencia C4 {a} -> {b} ('{d}') sin equivalente en paquetes.puml")
    for a, b in sorted(pkg - cubiertas):
        e.append(f"Dependencia del Lab 05 {a} -> {b} no está en el modelo C4")
    res["E3 componentes (coherencia con paquetes.puml, sin ciclos)"] = e

    # E4 dinámica -----------------------------------------------------------------
    e = []
    din = [v for v in vistas if v["tipo"] == "dynamic"]
    if not din: e.append("Falta la vista dynamic")
    else:
        pasos = din[0]["pasos"]
        if len(pasos) < 4: e.append(f"La vista dinámica requiere ≥ 4 pasos (hay {len(pasos)})")
        existentes = {(x["o"], x["d"]) for x in rel}
        for o, d in pasos:
            if (o, d) not in existentes:
                e.append(f"Paso {o} -> {d} no corresponde a una relación del modelo")
    res["E4 vista dinámica"] = e

    # E5 despliegue ---------------------------------------------------------------
    e = []
    faltan = set(cont) - desp["instancias"]
    if faltan: e.append(f"Contenedores sin containerInstance: {sorted(faltan)}")
    if desp["profundidad"] < 2: e.append("Se requieren nodos de despliegue anidados")
    if not any("2 vcpu" in t.lower() and "4 gb" in t.lower() for _, t in desp["nodos"]):
        e.append("Ningún nodo declara 2 vCPU y 4 GB RAM (R-03 de drivers.md)")
    if not any(v["tipo"] == "deployment" for v in vistas): e.append("Falta la vista deployment")
    res["E5 despliegue (coherente con R-03)"] = e

    fallo = False
    for k, errs in res.items():
        print(f"{k}: {'OK' if not errs else 'FALLA'}")
        for x in errs:
            fallo = True
            print("   -", x)
    print(f"\n{len(personas)} personas, {len(ext)} externos, {len(cont)} contenedores, {len(comps)} componentes, "
          f"{len(rel)} relaciones, {len(vistas)} vistas")
    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main())
