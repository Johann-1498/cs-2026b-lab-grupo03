# Bitácora de uso de IA – Laboratorio 06 (modelo C4, EcoRecicla AQP)

> Regla de oro: la IA propone, el equipo decide y verifica. No se ingresaron datos personales ni confidenciales en
> ningún prompt.

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 16/10/2026 | Claude (Anthropic) | **Prompt IA 1 adaptado:** borrador de `workspace.dsl` a partir de `inventario.md`, ADR-001/002/003 y `despliegue.py`; 5 vistas; usar solo tecnologías de los ADR; `!identifiers hierarchical`. | Modelo con 3 personas, 2 sistemas externos, 6 contenedores, 7 componentes (los paquetes del Lab 05) y las 5 vistas; Nginx y monitoreo como nodos de infraestructura, no como contenedores. | Se comprobó que no hubiera Docker, Kafka ni servicio de mapas (E2). `structurizr validate` falló con `The source element "webInst" does not exist`: con identificadores jerárquicos las instancias del despliegue se referencian por su ruta (`nav.webInst`, `vps.monolito.apiInst`). | Aceptada con corrección; `validate` termina sin errores. |
| 2 | 16/10/2026 | Claude (Anthropic) + Structurizr CLI + PlantUML | Exportar a C4-PlantUML y Mermaid, renderizar los PNG y revisarlos con la lista oficial. | Cinco vistas exportadas (10 archivos) y sus imágenes. | (a) El exportador dejó `$tags=""` y dibujó los sistemas externos como propios: se creó `scripts/c4_postproceso.py` (`System` → `System_Ext`). (b) En el despliegue aparecían flechas directas de la web/PWA a la API saltándose a Nginx: se etiquetaron `ViaProxy` y se excluyen de esa vista. (c) La vista dinámica no mostraba que el worker toma la tarea de la cola: se agregó el paso. | Aceptada con correcciones. |
| 3 | 16/10/2026 | Claude (Anthropic) | **Prompt IA 3:** explicar el contexto al presidente de la asociación en ≤ 120 palabras, sin jerga. | Texto de 115 palabras sobre qué hace el sistema, quién lo usa y de qué servicios depende. | Se contrastó cada afirmación con el modelo (tabla en `explicacion.md`) y se contó la longitud. Se verificó que no prometa pagos (EcoRecicla acredita puntos, no cobra). | Aceptada. |
| 4 | 16/10/2026 | Claude (Anthropic) | Escribir `verificar_c4.py`: contrastar el modelo con la lista de revisión, los ADR y `docs/design/paquetes.puml` (componentes iguales, sin ciclos, pasos dinámicos existentes). | Script que lee `workspace.dsl` y `paquetes.puml` y verifica E1–E5. | Su primera ejecución marcó `rutas → infraestructura` "sin equivalente" en `paquetes.puml`. Análisis: C4 muestra uso en ejecución; el Lab 05 muestra dependencia de compilación (ADR-004: puerto `RepositorioSolicitudes` de `solicitudes`). Se formalizó la regla de correspondencia por puertos y se comprobó con mutaciones (ciclo, Kafka, relación sin protocolo) que el script falla cuando debe. | Aceptada con ajuste (regla de puertos documentada). |
| 5 | 16/10/2026 | Claude (Anthropic) | **Prompt IA 2 (auditor C4)** sobre las cinco vistas con la lista oficial. | 8 hallazgos (ver `revision-c4.md`). | 2 falsos positivos: un "ciclo" `solicitudes ↔ rutas` (confunde uso en ejecución con dependencia de compilación) y un "error de alcance" por mostrar contenedores vecinos en la vista de componentes. 1 error real corregido: flechas persona → contenedor con la etiqueta vaga "Usa". | Parcialmente aceptada (1 corregido, 2 rechazados, 4 aceptados con justificación). |
| 6 | 16/10/2026 | Claude (Anthropic) | Comparar `contexto-manual.puml` con el modelo exportado y medir qué pasa si cambia el nombre de un contenedor. | Tabla comparativa y propuesta de experimento. | Se midieron los datos: 20 líneas a mano frente a 175 del DSL (5 vistas); pipeline de ≈ 16 s; el nombre de `Cola y caché` aparece 10 veces en 8 archivos exportados frente a 1 línea del DSL. | Aceptada (ver `comparacion.md`). |

## Anexo: prompts completos

### Prompt 1 – Borrador del modelo en Structurizr DSL (Prompt IA 1 adaptado)
```text
Actúa como arquitecto de software experto en el modelo C4 y en Structurizr DSL.
Contexto: [pegar inventario.md, ADR-001, ADR-002, ADR-003 y despliegue.py de EcoRecicla AQP].
Tarea: escribe un workspace de Structurizr DSL con personas, el sistema, sus contenedores (con tecnología),
los componentes del contenedor API (los paquetes de docs/design/paquetes.puml), los sistemas externos
(con la etiqueta "Externo") y relaciones con descripción y protocolo. Incluye las vistas systemContext,
container, component, dynamic (solicitar recojo) y deployment (entorno "Producción").
Restricciones: usa SOLO las tecnologías de los ADR y de despliegue.py; no confundas contenedor C4 con
contenedor Docker; usa !identifiers hierarchical. Formato: solo el código DSL.
```

### Prompt 2 – Auditor C4
```text
Actúa como revisor de diagramas de arquitectura. Evalúa estas vistas exportadas de un modelo C4
[pegar los .puml o adjuntar las imágenes] con la lista de revisión de c4model.com: generales, elementos y
relaciones. Responde en una tabla (vista, pregunta de la lista, cumple sí/no, evidencia, corrección sugerida).
No inventes problemas: si algo cumple, indícalo.
```

### Prompt 3 – Explicación para público no técnico
```text
Explica el siguiente diagrama de contexto al presidente de la asociación de recicladores, que no es técnico,
en máximo 120 palabras: qué hace el sistema, quién lo usa y de qué servicios externos depende. Evita la jerga
técnica. [pegar la vista de contexto]
```

### Prompt 4 – Verificador de coherencia
```text
Escribe un script de Python que lea workspace.dsl y docs/design/paquetes.puml y verifique: (1) la lista de
revisión (título, descripción, tecnología, etiqueta y protocolo de cada relación); (2) que los contenedores
usen solo tecnologías de los ADR; (3) que los componentes sean los paquetes del Lab 05 y no formen ciclos;
(4) que cada paso de la vista dinámica sea una relación existente; (5) que cada contenedor tenga una
instancia en el despliegue y que el VPS declare 2 vCPU y 4 GB RAM.
```

### Prompt 5 – Comparación de enfoques
```text
Compara escribir a mano el diagrama de contexto con C4-PlantUML frente a exportarlo desde Structurizr DSL en:
esfuerzo, errores encontrados y qué pasa si mañana cambia el nombre de un contenedor. Usa datos medidos.
```
