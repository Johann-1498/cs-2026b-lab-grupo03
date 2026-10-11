# Bitácora de uso de IA – Laboratorio 05 (EcoRecicla AQP)

> Regla de oro: la IA propone, el equipo decide y verifica. Nunca se ingresaron datos personales
> ni confidenciales en los prompts (los nombres de vecinos/recicladores del diseño son genéricos).

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 10/10/2026 | Claude (Anthropic) | **Prompt IA 1 adaptado:** diagrama de clases PlantUML de HU-03 (solicitar recojo) con atributos tipados, operaciones, multiplicidades, 1 enumeración y puertos, respetando el ADR-001. | Diagrama con 6 módulos de dominio. Planteamiento inicial con asociaciones directas entre clases de módulos distintos (`Solicitud`→`Reciclador`, `CuentaPuntos`→`Vecino`) y `TipoMaterial` dentro de `solicitudes`. | Las asociaciones cruzadas violan el ADR-002 (sin acoplar tablas entre módulos) y crean un ciclo `solicitudes` ↔ `rutas`; `TipoMaterial` lo usan también `puntos` y `rutas` (pasó a `compartido`). | Corregida: referencias por id (`recicladorId`, `vecinoId`), nuevo paquete `compartido` y ADR-004. |
| 2 | 10/10/2026 | Claude (Anthropic) | Diagrama de secuencia PlantUML de "solicitar recojo": ≥ 5 líneas de vida, `alt`, `loop`/`opt`, mensaje asíncrono y retornos; cada mensaje debe existir en `clases.puml`. | Secuencia con `alt` (cobertura/sin cobertura), `loop` por material, `opt` si hay reciclador y `->>` para `notificarAsignacion`. | Se cruzó cada mensaje con `clases.puml` (C1) con el script del equipo (sin hallazgos) y se hizo una prueba de mutación (mensaje inventado `reasignarTodo`) para confirmar que el verificador sí detecta violaciones. Se comprobó que `materialesValidos()` cubra el criterio CA-2 (rechazar solicitudes sin materiales). | Aceptada. |
| 3 | 10/10/2026 | Claude (Anthropic) | Diagrama de actividades "ruta diaria del reciclador" con 3 particiones, ≥ 2 decisiones y `fork`/`join`; incluir el caso sin conectividad (QA fiabilidad). | Flujo Sistema–Reciclador–Vecino con decisiones "¿vecino ausente?" y "¿hay conexión?" y un `fork` para acreditar puntos y notificar. | La primera versión ubicaba la decisión en el carril *Vecino* y PlantUML dibujó los rótulos `sí`/`no` invertidos respecto de las ramas. Se movió la decisión al carril *Reciclador* y se reordenaron las ramas; se re-renderizó y revisó el PNG. | Corregida. |
| 4 | 10/10/2026 | Claude (Anthropic) | **Prompt IA 2:** esqueleto en Python 3.10 (dataclasses, type hints, ABC) de `clases.puml`; mismos nombres en snake_case, adaptadores con `NotImplementedError`. | Paquetes `solicitudes`, `rutas`, `distritos`, `puntos`, `compartido`, `infraestructura`, con máquina de estados en `Solicitud` y estrategia `ReglaPuntosPorKg`. | Se ejecutaron 25 pruebas (una por transición + criterios CA-1…CA-4 + QA-01). Se eliminó un valor mágico (`Decimal("0.001")`) que la IA usó para materiales no declarados (lógica no pedida) y se agregó el puerto `listar_por_reciclador`, que `ServicioRutas` necesitaba. | Aceptada con correcciones. |
| 5 | 10/10/2026 | Claude (Anthropic) | **Prompt IA 3 (auditor):** revisar C1–C5 sobre los 5 diagramas y responder en tabla citando la línea. | 7 hallazgos (C1, C2, C3, C4, C5). | Se verificó cada uno con el script `verificar_consistencia.py` y lectura manual: 3 falsos positivos (`<<create>>`, "ciclo" solicitudes↔rutas, asociaciones por id), 1 error real (`confirmarRecojo` duplicado) y 3 observaciones aceptadas. Ver `consistencia.md`. | Parcialmente aceptada (1 corregido, 3 rechazados, 3 documentados). |
| 6 | 10/10/2026 | Claude (Anthropic) + pyreverse | Comparar el diagrama de diseño con el de `pyreverse` y proponer acciones. | Tabla con 9 diferencias (causa y acción). | `pyreverse` falló al inicio con "No module named \_\_init\_\_" porque `src/` no es paquete; se invocó por módulo. Se corrigió el diagrama (`pesajesReales`, `acreditadas`) y se documentaron las limitaciones de la herramienta. Ver `round-trip.md`. | Aceptada con ajustes. |

## Anexo: Prompts completos

### Prompt 1 – Diagrama de clases (Prompt IA 1 adaptado)
```text
Actúa como diseñador de software orientado a objetos. Contexto: módulos Solicitudes, Rutas, Puntos
y Distritos de EcoRecicla AQP, un monolito modular en Django (ADR-001: puertos y adaptadores para
integraciones externas; los módulos se comunican solo por services.py; ADR-002: sin consultas ni
claves foráneas cruzadas entre módulos). Historia y criterios: [pegar historia.md].
Tarea: genera un diagrama de clases en PlantUML con atributos tipados, operaciones, multiplicidades,
una enumeración para el estado de la solicitud y una interfaz (puerto) para las notificaciones.
Formato: solo el código PlantUML. No agregues clases que no se deriven de la historia; si asumes
algo, indícalo en un comentario. No incluyas datos sensibles innecesarios del vecino.
```

### Prompt 2 – Diagrama de secuencia
```text
Con el siguiente clases.puml: [pegar]. Dibuja en PlantUML el diagrama de secuencia del escenario
principal de HU-03 (solicitar recojo). Requisitos: 5 o más líneas de vida (actor, UI, controlador,
servicio, entidades y puertos), un fragmento alt para éxito y error, un loop u opt, al menos un
mensaje asíncrono (->>) y los mensajes de retorno. Cada mensaje dirigido a un objeto debe ser una
operación de su clase en clases.puml; si falta alguna, indícala sin inventarla.
```

### Prompt 3 – Diagrama de actividades
```text
Modela en PlantUML el proceso "ruta diaria del reciclador" de EcoRecicla AQP con particiones
(|Sistema|, |Reciclador|, |Vecino|), 2 o más decisiones (if/else) y un fork/end fork. Considera
que en campo puede no haber conexión 3G (fiabilidad) y que el registro debe tomar 4 toques o menos.
```

### Prompt 4 – Ingeniería directa (Prompt IA 2)
```text
Genera el esqueleto en Python 3.10 (dataclasses y type hints) del siguiente diagrama de clases.
Respeta exactamente los nombres de clases, atributos y operaciones (en snake_case), las
enumeraciones, la interfaz como clase abstracta (ABC) y las multiplicidades. Implementa solo la
lógica mínima de las operaciones de Solicitud; los adaptadores deben lanzar NotImplementedError.
Un paquete por módulo del ADR-001 más compartido e infraestructura. [pegar clases.puml]
```

### Prompt 5 – Auditor de consistencia (Prompt IA 3)
```text
Actúa como revisor de diseño. Te paso cinco diagramas UML en PlantUML/Mermaid: [pegar los cinco
archivos]. Verifica estas reglas y responde en una tabla (regla, elemento, problema, corrección
sugerida): C1 cada mensaje de secuencia es una operación de la clase receptora; C2 cada transición
de estados corresponde a una operación de la clase; C3 multiplicidades coherentes con los
criterios de aceptación; C4 paquetes sin ciclos; C5 nombres consistentes. No reescribas los
diagramas; solo reporta hallazgos y cita la línea.
```

### Prompt 6 – Comparación round-trip
```text
Te paso classes_ecorecicla_pyreverse.puml (generado del código) y clases.puml (diseño). Lista
las diferencias (qué falta, qué sobra, qué cambió de nombre), su causa probable (limitación de
pyreverse, convención de Python o error de generación) y la acción recomendada: corregir el
diagrama, corregir el código o documentar la limitación.
```
