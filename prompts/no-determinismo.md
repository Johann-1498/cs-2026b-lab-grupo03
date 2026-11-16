# No determinismo (E7.3 – obligatorio)

> **ESTE ARCHIVO LO DEBE COMPLETAR EL GRUPO** con ejecuciones reales. No se rellenó con datos inventados.

Procedimiento: ejecutar la **mejor versión** (`prompts/criterios/v4.txt`) **3 veces** en el asistente del grupo
(chat nuevo en cada vez) sobre los mismos 3 casos (H1, H7 y H9). Guardar las respuestas **sin editar** en
`prompts/criterios/no-determinismo/run{1,2,3}/<id>.txt` y pasarlas por las aserciones A1–A6.

| Caso | Corrida 1 | Corrida 2 | Corrida 3 | ¿Mismo resultado de aserciones? | ¿Mismo texto? |
|---|---|---|---|---|---|
| H1 | | | | | |
| H7 | | | | | |
| H9 | | | | | |

Escriban 5 líneas respondiendo: (1) qué cambió entre corridas (redacción, número de escenarios, datos de
ejemplo); (2) qué no cambió (estructura, `invest_ok`); (3) qué implica para las grabaciones: una grabación
es una **foto** de un momento, no una garantía; (4) por qué la CI con proveedor grabado es reproducible pero
no detecta que el modelo real cambie; (5) qué se haría con un modelo real (temperatura 0, varias muestras y
umbral de aprobación en vez de igualdad de texto).
