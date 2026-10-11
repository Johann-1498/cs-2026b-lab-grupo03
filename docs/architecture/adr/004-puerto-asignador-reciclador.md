# ADR-004: Invertir la dependencia solicitudes ↔ rutas con el puerto AsignadorReciclador

- Estado: Aceptado
- Fecha: 2026-10-10
- Decisores: Equipo de desarrollo (3 devs)

## Contexto

Al modelar el diagrama de paquetes del Laboratorio 05 (`docs/design/paquetes.puml`) apareció un
**ciclo** entre dos módulos del ADR-001:

- `solicitudes` necesita **asignar un reciclador** cuando se registra una solicitud (HU-03, CA-1), es
  decir, llamar a `rutas`.
- `rutas` necesita **leer las solicitudes ASIGNADAS** para generar la ruta del día (RF-02), es decir,
  depender de `solicitudes`.

Con ambas flechas (`SOL ..> RUT` y `RUT ..> SOL`) los dos paquetes forman en la práctica un solo
módulo, lo que contradice la regla C4 (sin ciclos) y erosiona la modificabilidad (**QA-01**). El
ciclo también habría producido dependencias circulares entre migraciones (riesgo ya señalado en el
ADR-002).

## Alternativas consideradas

1. Fusionar `solicitudes` y `rutas` en un solo módulo: elimina el ciclo, pero pierde la separación
   de dominios definida en el ADR-001 y concentra demasiada responsabilidad en un módulo.
2. Que `rutas` reciba las solicitudes por parámetro y `solicitudes` no la conozca: obliga a que
   un tercero orqueste la asignación y mueve el ciclo a la capa de presentación.
3. **Puerto `AsignadorReciclador` definido en `solicitudes` y realizado por `ServicioRutas`**:
   `solicitudes` depende solo de una interfaz propia; `rutas` depende de `solicitudes` (no al revés).
   Es el mismo patrón de puertos y adaptadores del ADR-001, aplicado entre módulos internos: elegida.

## Decisión

Se define la interfaz `AsignadorReciclador` (`asignar(s: Solicitud): UUID`) en
`solicitudes/puertos.py`. `ServicioRutas` (módulo `rutas`) la **realiza**. `ServicioSolicitudes`
recibe el asignador por inyección y nunca importa `rutas`. La dirección de la dependencia
en tiempo de compilación queda `rutas → solicitudes`.

Además, `solicitudes` y `rutas` se referencian entre sí solo por identificador
(`Solicitud.recicladorId: UUID`), sin asociaciones entre clases de módulos distintos (ADR-002).

## Consecuencias

- Positivas: grafo de paquetes acíclico (C4 verificado con `scripts/verificar_consistencia.py`);
  se puede probar `ServicioSolicitudes` con un asignador falso; cambiar el algoritmo de
  asignación (por ejemplo, por cercanía) no toca `solicitudes`.
- Negativas / riesgos: un nivel más de indirección; en los diagramas de secuencia la flecha
  `solicitudes → rutas` parece una dependencia, por lo que debe explicarse (el diagrama de
  paquetes es la fuente de verdad de las dependencias).
