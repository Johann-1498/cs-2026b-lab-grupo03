# Historia de usuario crítica – EcoRecicla AQP

> Caso 10 de la Tabla 7 del Laboratorio 05. Continúa el diseño del Laboratorio 04
> (ADR-001: monolito modular con puertos y adaptadores; módulos `solicitudes`, `rutas`,
> `puntos`, `reportes` y `distritos`).

```text
HU-03: Como vecino, quiero solicitar el recojo de mis reciclables indicando el tipo
       de material, mi dirección y una franja horaria, para que un reciclador
       formalizado los recoja en mi domicilio y yo acumule puntos ecológicos.
```

## Criterios de aceptación

- **CA-1 (éxito).** **Dado** un vecino con una dirección en un distrito con cobertura activa,
  **cuando** registra una solicitud con al menos un material (tipo y peso estimado) y una
  franja horaria, **entonces** la solicitud se crea en estado `PENDIENTE`, el sistema le asigna
  un reciclador disponible del distrito (`ASIGNADA`) y se notifica la asignación.
- **CA-2 (error).** **Dado** un vecino con una dirección en un distrito sin cobertura, o una
  solicitud sin materiales, **cuando** intenta registrarla, **entonces** el sistema la rechaza
  con un mensaje claro y **no** se crea ninguna solicitud.
- **CA-3 (atención).** **Dado** una solicitud `ASIGNADA`, **cuando** el reciclador confirma el
  recojo y registra el pesaje (kg por tipo de material), **entonces** la solicitud pasa por
  `RECOGIDA` y `PESADA` hasta `PUNTOS_ACREDITADOS`, y el vecino recibe los puntos calculados
  con la regla vigente de su distrito.
- **CA-4 (sin recojo).** **Dado** una solicitud `ASIGNADA`, **cuando** el reciclador no puede
  recoger (vecino ausente), **entonces** la solicitud vuelve a `PENDIENTE` para reasignarse.

## Trazabilidad con los drivers del Laboratorio 04

| Criterio | Requisito | Atributo de calidad / restricción |
|---|---|---|
| CA-1, CA-2 | RF-01, RF-06 | R-04 (Ley N.º 29733: solo se guarda el celular del vecino) |
| CA-3 | RF-03, RF-04 | QA-01 (la regla de puntos es una estrategia intercambiable por distrito) |
| CA-4 | RF-02 | Fiabilidad (ninguna solicitud se pierde) |

## Alcance y supuestos

- Alcance: solo lo necesario para HU-03 (MVP de 1 mes, R-01).
- Supuesto: los puntos por kilo (PLASTICO 10, PAPEL_CARTON 5, VIDRIO 4, METAL 12) son valores de
  ejemplo configurables por distrito; la Municipalidad los define.
- Supuesto: el canal de notificación (WhatsApp, SMS o push) se decide en el adaptador; el diseño
  solo conoce el puerto `Notificador`.
