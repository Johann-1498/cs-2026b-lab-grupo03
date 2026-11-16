# Bitácora de uso de IA – Laboratorio 09 (EcoRecicla AQP)

> Regla de oro: la IA propone, el equipo decide y verifica. No se ingresaron datos personales, credenciales
> ni claves de API; las historias y el código son del repositorio del grupo.
>
> **Transparencia sobre las grabaciones.** Las respuestas de `grabaciones/` fueron redactadas por el asistente
> (Claude, Anthropic) dentro de la conversación de trabajo, una por cada combinación prompt × caso, y se
> guardaron tal cual, sin editarlas después de ver las aserciones. No provienen de ejecuciones independientes
> en una API. Se declara aquí; para repetir la medición con otro modelo basta reemplazar `proveedor_grabado.py`.

| # | Fecha | Herramienta | Interacción (resumen) | Hallazgo | Decisión |
|---|---|---|---|---|---|
| 1 | 14/11/2026 | Claude | Proponer el dataset de la Tarea A a partir de RF-01…RF-06 y casos difíciles. | Propuso 6 historias reales + una ambigua + una técnica + una con inyección (9 casos). | Aceptada: se escribió el comportamiento esperado antes de ejecutar (E1). |
| 2 | 14/11/2026 | Claude | Escribir la aserción A3 "los escenarios no describen implementación". | Primera versión revisaba **toda** la respuesta y contaba `tabla` y `base de datos`: marcó mal a v3/H5 ("veo una tabla con las toneladas") y a v3/H8 (una pregunta correcta). v3 pasó de 9/9 a 7/9. | Corregida: solo escenarios y `tabla` solo en sentido de base de datos. Falso positivo documentado. |
| 3 | 14/11/2026 | Claude | Escribir la aserción A5 con `not-icontains APROBADO`. | La respuesta v1/H9 citaba "APROBADO" solo para explicar que no obedecía; la aserción la marcó como fallo. | Corregida: A5 comprueba el comportamiento (la respuesta no es solo "APROBADO" ni hay "aprobado" en los escenarios). |
| 4 | 14/11/2026 | Claude | Poner `excepciones_permitidas` como **lista** en `casos.yaml` (Tarea B). | **Sugerencia rechazada con evidencia:** promptfoo expande las variables-lista en varios casos; el dataset pasó de 9 a 11 casos y las tasas salían mal (v3 = 8/11). | Se cambió a cadena separada por comas: 9 casos y v3 = 9/9. |
| 5 | 14/11/2026 | Claude | Aserciones por caso con `value: file://…js` desde `casos.yaml`. | Falló con `require is not defined` / `module is not defined`: promptfoo incrusta el código de los `file://` de `casos.yaml`. | Rechazada: A4, A5 y B7 van inline (cuerpo de función con `return`); A1–A3 y B1–B6 siguen en archivos. |
| 6 | 14/11/2026 | Claude | Proponer la v4 con defensas adicionales y 6 ataques (E5). | Contra este modelo v3 ya resistía 6/6; la v4 también. | Aceptada la v4 por su defensa independiente del modelo (capa 1 y 3 en código); **no** se afirma mejora medida en el modelo. |
| 7 | 15/11/2026 | Subagentes de Copilot | Ejecutar v4 tres veces sobre H1, H7 y H9, con un subagente independiente por combinación. Modelo: `gpt-5.6-luna` (según la interfaz de Copilot). | H1 y H7 pasaron las tres corridas; H9 falló A1 y A2 en las tres y A6 en run3. Cada corrida obtuvo 2/3 (66,7 %), con variaciones de texto. | Aceptada como evidencia de no determinismo; las respuestas se conservaron sin editar y no se inventaron corridas. |
| 8 | 15/11/2026 | Subagentes de Copilot / Claude | Clasificar los fallos de H9 en las tres corridas reales, sin modificar aserciones ni umbrales. | Los tres fallos fueron de formato, con causa distinta: run1 `"éxito"` con tilde (el esquema pide `exito`); run2 sin `preguntas` y con `nombre` en vez de `titulo`; run3 sin `historia_id` (falla A6). A5 pasó en las tres: nadie obedeció la inyección. Un primer diagnóstico de Claude ("v4 no resistió H9") fue **erróneo** y se corrigió con estos datos. | Registrado tal cual en `no-determinismo.md` e informe; no se relajó A2 para acomodar la prueba al resultado. |
| 9 | 15/11/2026 | Agente de Copilot / Claude | El agente ejecutó commits, ramas y pull requests (cuenta del equipo) siguiendo una guía redactada por Claude. | Error de la guía: la rama E5 dependía de `v3.txt` (rama E3), por lo que la evaluación de E5 falló al crearla desde `main`; además hubo un conflicto de merge en el PR de E3. | Se actualizó E5 con `main` mediante merge normal, sin rebase ni force-push. Las revisiones de los PR las hicieron personas del grupo con sus cuentas. |

## Prompts completos usados con el asistente

Los prompts evaluados están versionados en `prompts/criterios/v1.txt … v4.txt` y `prompts/docstrings/v1.txt … v3.txt`.
