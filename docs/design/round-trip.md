# Round-trip: del diagrama al código y de vuelta – EcoRecicla AQP

Flujo aplicado (Figura 3 de la guía): `clases.puml` → IA (ingeniería directa) → `src/` →
`pyreverse` (ingeniería inversa) → `classes_ecorecicla_pyreverse.puml` → comparación humana → corrección.

## Comandos ejecutados

```bash
# Ingeniería directa: Prompt IA 2 (ver bitacora-ia.md, interacción 4) → src/<modulo>/
pip install pylint pytest
export PYTHONPATH=src
# Ingeniería inversa (pyreverse necesita los paquetes; src/ no tiene __init__.py propio)
pyreverse -o puml -p ecorecicla -d docs/design \
    src/compartido src/solicitudes src/rutas src/distritos src/puntos src/infraestructura
#   → classes_ecorecicla.puml y packages_ecorecicla.puml (renombrados *_pyreverse.puml)
java -jar plantuml.jar -tpng -o img classes_ecorecicla_pyreverse.puml paquetes_ecorecicla_pyreverse.puml
pytest tests                       # 25 pruebas en verde
python scripts/verificar_consistencia.py   # C1–C5 automáticos
```

Imágenes: `img/classes_ecorecicla.png` (clases) e `img/packages_ecorecicla.png` (paquetes).

## Tabla de diferencias (diagrama de diseño vs. diagrama obtenido del código)

| # | Diferencia observada | Causa | Acción |
|---|---|---|---|
| 1 | No aparece la composición `Solicitud *-- ItemMaterial` (1 a 1..\*); las líneas figuran como atributo `items : list[ItemMaterial]`. | pyreverse no infiere asociaciones desde colecciones tipadas. | **Documentar la limitación.** El diagrama de diseño se mantiene como fuente de verdad. |
| 2 | Ninguna asociación muestra multiplicidades (`1`, `0..*`, `1..*`). | El código no expresa multiplicidades. | **Corregir el código:** `ServicioSolicitudes._materiales_validos()` exige ≥ 1 material (C3) y la prueba `test_CA2b_sin_materiales_no_crea_solicitud` lo comprueba. |
| 3 | `AsignadorReciclador`, `Notificador`, `RepositorioSolicitudes` y `ReglaPuntos` aparecen como `class` con métodos `{abstract}` (no como `interface`); `NotificadorAdapter` y `RepositorioSolicitudesORM` también muestran sus métodos como abstractos. | Python implementa interfaces con `ABC`; los adaptadores aún lanzan `NotImplementedError`, por lo que pyreverse los marca abstractos. | **Documentar.** Aceptable en Python; se resolverá al integrar el ORM y el proveedor de notificaciones. |
| 4 | Por defecto pyreverse oculta miembros privados: no aparecen `_materiales_validos()`, `_exigir()` ni las dependencias inyectadas (`_repo`, `_notificador`, `_asignador`, `_distritos`, `_puntos`). Con `-f ALL` aparecen, pero como **agregación** (`--o`) y no como dependencia de uso (`..>`). | Convención de visibilidad de pyreverse y diferencia entre atributo inyectado (agregación en código) y dependencia (en el diseño). | **Documentar.** Se mantiene `..>` en el diseño porque los servicios no son "dueños" de los puertos que reciben por inyección. |
| 5 | La asociación `Vecino "1" -- "0..*" Solicitud` no aparece: `Vecino` queda aislado y `Solicitud` guarda `vecino_id : UUID`. | El código referencia al vecino por identificador, no por objeto (coherente con ADR-002: sin acoplar tablas). | **Documentar.** La asociación del diseño es conceptual; en el código es una referencia por id. |
| 6 | El código tiene `Solicitud._exigir()` (guarda de transición), `Solicitud.pesajes_reales()`, `CuentaPuntos.acreditadas` (idempotencia) y las excepciones `TransicionInvalida` y `SolicitudInvalida` (en rojo en pyreverse) que el diseño no tenía. | La IA agregó lógica de apoyo no pedida al generar el esqueleto. | **Corregir el diagrama:** se agregaron `pesajesReales()` y `acreditadas` a `clases.puml`. `_exigir()` y las excepciones se documentan como detalle de implementación. |
| 7 | Los nombres cambian de camelCase a snake_case (`calcularTotal` → `calcular_total`, `solicitarRecojo` → `solicitar_recojo`, `distritoId` → `distrito_id`). | Convención PEP 8 de Python. | **Documentar la equivalencia** (C5): se traduce con `snake()` en `verificar_consistencia.py`. |
| 8 | En el diagrama de paquetes de pyreverse falta `reportes` y las dependencias `REP ..> *`; además no hay etiquetas ni la nota de la regla. | `reportes` está fuera del alcance de HU-03 y aún no tiene código; pyreverse no genera etiquetas. | **Documentar.** Las dependencias reales sí coinciden con `paquetes.puml` (ver abajo) y no hay ciclos. |
| 9 | Los atributos de tipo clase/enumeración (`tipo`, `estado`) aparecen sin tipo en el compartimento y solo como flecha de asociación; las enumeraciones muestran un miembro genérico `name` en lugar de sus valores (`PENDIENTE`, `ASIGNADA`, …). | pyreverse trata `Enum` como una clase con el atributo heredado `name`. | **Documentar.** Los valores de `EstadoSolicitud` se verifican con `verificar_consistencia.py` (C2) contra el `.mmd`. |

## Comprobación del diagrama de paquetes (regla C4)

Aristas entre módulos obtenidas del código (`packages_ecorecicla.puml`) comparadas con `paquetes.puml`:

| Arista | En el diseño | En el código |
|---|---|---|
| `solicitudes → distritos` | Sí | Sí (`solicitudes.services → distritos.services`) |
| `solicitudes → puntos` | Sí | Sí (`solicitudes.services → puntos.services`) |
| `rutas → solicitudes` | Sí | Sí (`rutas.services → solicitudes.dominio / puertos`) |
| `infraestructura → solicitudes` | Sí | Sí (`infraestructura.adaptadores → solicitudes.*`) |
| `solicitudes → compartido`, `puntos → compartido` | Sí | Sí |
| `solicitudes → rutas` | **No** (ADR-004) | **No** |
| `reportes → *` | Sí | No hay código todavía |

El código no introduce ninguna dependencia que el diseño no tenga, y el grafo es acíclico.

## Qué aprendimos

- La ingeniería inversa **no reemplaza** al diagrama de diseño: pierde multiplicidades, composiciones
  y la intención (puertos, estrategias).
- Sí sirve para detectar lógica agregada por la IA y para comprobar que las dependencias de
  paquetes del código coinciden con el ADR-001/ADR-004.
