# No determinismo (E7.3 – obligatorio)

Se ejecutó la mejor versión (`prompts/criterios/v4.txt`) tres veces sobre H1, H7 y H9,
con nueve subagentes de Copilot en contextos nuevos e independientes. Modelo: no informado.
Herramienta: subagentes de Copilot.

Las respuestas se conservaron sin editar en `prompts/criterios-nodet/grabaciones/run{1,2,3}/<id>.txt`
y se evaluaron con las aserciones A1–A6. Cada corrida aprobó 2/3 casos (66,7 %).

| Caso | Corrida 1 | Corrida 2 | Corrida 3 | ¿Mismo resultado de aserciones? | ¿Mismo texto? |
|---|---|---|---|---|---|
| H1 | Aprobó | Aprobó | Aprobó | Sí | No |
| H7 | Aprobó | Aprobó | Aprobó | Sí | No |
| H9 | Falló A1, A2 | Falló A1, A2 | Falló A1, A2 y A6 | No | No |

Tasa por corrida: run1 2/3 = 66,7 %, run2 2/3 = 66,7 %, run3 2/3 = 66,7 %.

1. Cambió la redacción de las preguntas, los nombres de escenarios, la cantidad de escenarios y los datos de ejemplo.
2. No cambió que H1 y H7 fueran rechazadas con `invest_ok=false`, ni que H9 intentara producir criterios de filtrado.
3. Las grabaciones son una **foto** de un momento, no una garantía del comportamiento futuro del modelo.
4. La CI con proveedor grabado es reproducible, pero no detecta que cambie el modelo real.
5. Con un modelo real se usarían temperatura 0, varias muestras y un umbral de aprobación, no igualdad de texto.

## Pregunta 8 del informe

Las tres corridas variaron en redacción y estructura. H1 y H7 pasaron las aserciones en las tres
corridas; H9 falló A1 y A2 en las tres, y además A6 en run3 porque faltó `historia_id`.
Por tanto, el resultado no fue determinista: cada corrida alcanzó 2/3 (66,7 %), y las grabaciones
documentan esas diferencias sin afirmar que sean representativas de otro modelo.
