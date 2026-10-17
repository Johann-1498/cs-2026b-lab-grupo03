#!/usr/bin/env bash
# Pipeline "arquitectura como código": valida, exporta, post-procesa y genera las imágenes.
# Requisitos: Java 17+, Structurizr CLI (STRUCTURIZR=ruta/structurizr.sh) y plantuml.jar (PLANTUML=ruta).
set -euo pipefail
cd "$(dirname "$0")/.."
STRUCTURIZR="${STRUCTURIZR:-structurizr.sh}"
PLANTUML="${PLANTUML:-plantuml.jar}"
C4=docs/architecture/c4

"$STRUCTURIZR" validate -w "$C4/workspace.dsl"
rm -f "$C4"/export/*
"$STRUCTURIZR" export -w "$C4/workspace.dsl" -f plantuml/c4plantuml -o "$C4/export"
"$STRUCTURIZR" export -w "$C4/workspace.dsl" -f mermaid -o "$C4/export"
python3 scripts/c4_postproceso.py
mkdir -p "$C4/img"
java -Djava.awt.headless=true -jar "$PLANTUML" -tpng -o ../img "$C4"/export/*.puml
java -Djava.awt.headless=true -jar "$PLANTUML" -tpng -o img "$C4/contexto-manual.puml"
python3 scripts/verificar_c4.py
