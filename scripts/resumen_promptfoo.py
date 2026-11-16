#!/usr/bin/env python3
"""Resume un resultados.json de promptfoo: tasa de aprobación por versión, por aserción y por caso.

Uso:
    python scripts/resumen_promptfoo.py prompts/criterios/resultados.json [--umbral 85 --version v3]
Con --umbral y --version devuelve código 1 si la tasa de esa versión es menor al umbral
(se usa en CI: las versiones históricas v1/v2 fallan a propósito y no deben romper el build).
Con --json imprime el resumen como JSON (lo consume el generador del gráfico).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict


def resumir(ruta: str) -> dict:
    datos = json.load(open(ruta, encoding="utf-8"))
    filas = datos["results"]["results"]
    por_version: dict[str, dict] = defaultdict(lambda: {"ok": 0, "total": 0})
    por_aserc: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"ok": 0, "total": 0}))
    por_caso: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for f in filas:
        version = f["prompt"]["label"].split(":")[0].strip()
        caso = f["vars"].get("id", "?")
        por_version[version]["total"] += 1
        por_version[version]["ok"] += 1 if f["success"] else 0
        fallos = []
        for metrica, puntaje in (f.get("namedScores") or {}).items():
            por_aserc[version][metrica]["total"] += 1
            por_aserc[version][metrica]["ok"] += 1 if puntaje >= 1 else 0
            if puntaje < 1:
                fallos.append(metrica.split("_")[0])
        if f.get("failureReason") == 2:
            fallos.append("ERROR")
        por_caso[caso][version] = fallos
    return {"version": dict(por_version),
            "aserciones": {v: dict(m) for v, m in por_aserc.items()},
            "casos": dict(por_caso)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("resultados")
    ap.add_argument("--umbral", type=float)
    ap.add_argument("--version")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = resumir(a.resultados)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("Tasa de aprobación por versión (casos que pasan TODAS las aserciones):")
        for v in sorted(r["version"]):
            x = r["version"][v]
            print(f"  {v:<6} {x['ok']}/{x['total']} = {100 * x['ok'] / x['total']:.1f} %")
        print("\nPor aserción:")
        for v in sorted(r["aserciones"]):
            print("  " + v + ": " + ", ".join(f"{m.split('_')[0]} {x['ok']}/{x['total']}" for m, x in sorted(r["aserciones"][v].items())))
        print("\nFallos por caso (× = aserciones que fallaron):")
        for caso in sorted(r["casos"]):
            print(f"  {caso}: " + " | ".join(f"{v}: {'ok' if not f else '× ' + ','.join(f)}" for v, f in sorted(r["casos"][caso].items())))
    if a.umbral is not None and a.version:
        x = r["version"].get(a.version)
        if not x:
            print(f"No hay resultados para {a.version}", file=sys.stderr)
            return 1
        tasa = 100 * x["ok"] / x["total"]
        if tasa < a.umbral:
            print(f"FALLO: {a.version} = {tasa:.1f} % < umbral {a.umbral} %", file=sys.stderr)
            return 1
        print(f"\nOK: {a.version} = {tasa:.1f} % >= umbral {a.umbral} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
