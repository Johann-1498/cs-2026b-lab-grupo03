# Revisión de consistencia (reglas C1–C5) – EcoRecicla AQP

Se aplicó el **Prompt IA 3** (ver `bitacora-ia.md`, interacción 5) a los cinco diagramas
(`clases.puml`, `secuencia-solicitar-recojo.puml`, `estados-solicitud.mmd`,
`actividades-ruta-reciclador.puml`, `paquetes.puml`). Los hallazgos se contrastaron con el
verificador automático `scripts/verificar_consistencia.py` (todas las reglas en verde tras las
correcciones) y con una lectura manual del equipo.

## Hallazgos de la IA y verificación del equipo

| # | Regla | Elemento (línea) | Hallazgo de la IA | Verificación del equipo | Decisión |
|---|---|---|---|---|---|
| 1 | C1 | `secuencia-solicitar-recojo.puml:24` (`S -> P : <<create>>`) | "El mensaje `<<create>>` hacia `Solicitud` no es una operación declarada en la clase." | **Falso positivo.** En UML la creación de un objeto equivale a invocar su constructor, que no se declara como operación; el estereotipo `<<create>>` es notación estándar. Los mensajes posteriores (`agregarMaterial`, `asignar`) sí existen en `Solicitud`. | Rechazado |
| 2 | C4 | `secuencia-solicitar-recojo.puml:30` (`S -> A : asignar(solicitud)`) y `paquetes.puml:19` | "`solicitudes` llama a `rutas` y `rutas` depende de `solicitudes`: hay un ciclo." | **Falso positivo.** El mensaje 10 va al puerto `AsignadorReciclador`, que **pertenece a `solicitudes`** y es realizado por `ServicioRutas`. La dependencia de compilación es solo `RUT ..> SOL` (ADR-004). El verificador C4 no encuentra ciclos y `pyreverse` confirma que `solicitudes` no importa `rutas`. | Rechazado |
| 3 | C3 | `clases.puml:41` (`recicladorId`) | "Falta la asociación `Solicitud`–`Reciclador` con multiplicidad; `CuentaPuntos`–`Vecino` tampoco existe." | **Falso positivo de diseño.** Las clases de módulos distintos se referencian por identificador (ADR-002), para no crear dependencias ni claves foráneas cruzadas entre módulos. | Rechazado |
| 4 | C5 | `clases.puml:68` | "`confirmarRecojo()` existe en `Solicitud` y en `ServicioSolicitudes` con significados distintos (cambio de estado vs. flujo completo)." | **Correcto.** Genera ambigüedad entre el diagrama de estados (que usa `confirmarRecojo()`) y el servicio. | **Corregido:** el servicio pasa a llamarse `registrarRecojo()` en `clases.puml`, `services.py` y las pruebas. |
| 5 | C2 | `estados-solicitud.mmd:2` | "La transición inicial usa `solicitarRecojo()`, que no es operación de `Solicitud`." | **Parcialmente correcto.** El evento de creación pertenece al servicio (`ServicioSolicitudes.solicitarRecojo`); la regla C2 admite "una operación o un evento identificable de la clase". | Aceptado y documentado en este archivo |
| 6 | C2 | `estados-solicitud.mmd:3` | "La guarda `[reciclador disponible]` de `asignar()` no se valida dentro de `Solicitud.asignar()`." | **Correcto, pero intencional.** La guarda se evalúa en `ServicioSolicitudes` (fragmento `opt` de la secuencia, línea 32) y se prueba en `test_CA1b_sin_reciclador_disponible_queda_pendiente_sin_notificar`. | Aceptado |
| 7 | C1 | `secuencia-solicitar-recojo.puml:5-8` | "`PWA` y `SolicitudController` no existen en el diagrama de clases; los mensajes 2 y 3 no cumplen C1." | **Parcialmente correcto.** Son capa de presentación (API REST + PWA del ADR-001), fuera del alcance del diagrama de dominio; el mensaje 3 sí llega a `ServicioSolicitudes.solicitarRecojo`. | Aceptado; `verificar_consistencia.py` los excluye de forma explícita |

**Resumen:** 7 hallazgos → 3 falsos positivos (1, 2, 3), 1 error real corregido (4) y 3 observaciones
aceptadas con justificación (5, 6, 7). Ninguna regla queda sin cumplirse.

## Resultado final del verificador automático

```text
C1: OK
C2: OK
C3: OK
C4: OK
C5: OK
20 clases/interfaces/enums leídas de clases.puml
```

## Qué habría pasado si aceptábamos el hallazgo 2 sin verificar

Habríamos "arreglado" un ciclo inexistente moviendo `asignar()` a `rutas` o fusionando
`solicitudes` y `rutas`, perdiendo la separación de módulos del ADR-001 y la posibilidad de probar
`ServicioSolicitudes` con un asignador falso.
