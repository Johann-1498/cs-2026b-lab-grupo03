# Comparación: vista dinámica frente a secuencia UML (E4) y modelado frente a diagramación (E6)

## E4. Vista dinámica de C4 frente al diagrama de secuencia UML del Laboratorio 05

La secuencia UML (19 mensajes) muestra el detalle de ejecución: firmas de operaciones con parámetros
(`solicitarRecojo(vecinoId, …)`), la creación de `Solicitud`, los retornos, los fragmentos `alt`/`loop`/`opt`
y los códigos HTTP de éxito y error; sirve a los *developers* para implementar y probar. La vista dinámica
(8 pasos numerados) omite parámetros, retornos y alternativas, pero muestra por qué contenedor o componente
pasa el flujo (PWA, API, cola, worker, servicio externo); sirve al equipo técnico, a operaciones y a los
arquitectos para entender dónde ocurre cada paso. Se usa la dinámica para explicar el flujo y la secuencia
para programarlo.

## E6. Escritura a mano (`contexto-manual.puml`) frente al modelo exportado (`workspace.dsl`)

| Aspecto | C4-PlantUML a mano | Structurizr DSL (modelo único) |
|---|---|---|
| Esfuerzo de escritura | 20 líneas para **1** vista (contexto) | 175 líneas para **5** vistas + 5 exportaciones a PlantUML y 5 a Mermaid (243 líneas de PlantUML generadas) |
| Tiempo de máquina | Instantáneo | `c4_generar.sh` (validar, exportar 10 archivos, 6 PNG y verificar) tarda ≈ 16 s |
| Errores encontrados | Ninguno en el contexto (macros `System_Ext` correctas desde el inicio), pero nada garantiza coherencia con otras vistas | `validate` detectó un error real (`The source element "webInst" does not exist`: identificadores jerárquicos en el despliegue). El exportador `c4plantuml` dejó `$tags=""` y dibujó los sistemas externos como propios; se corrigió con `scripts/c4_postproceso.py` |
| Si mañana cambia el nombre de un contenedor | Hay que editar **cada** archivo donde aparece | Se edita **una** línea del DSL y se regenera |
| Coherencia entre vistas | Manual (riesgo de divergencia) | Automática: todas las vistas salen del mismo modelo |
| Verificación automática | No | `verificar_c4.py` recorre el modelo (ADR, paquetes del Lab 05, ciclos, protocolos) |

### Experimento: cambio de nombre

Se contó dónde aparece el contenedor `Cola y caché` en los archivos exportados: **10 apariciones en 8
archivos** (4 `.puml` y 4 `.mmd`; el contexto no lo incluye). Con diagramas sueltos habría que corregir
las 10; con Structurizr se cambia **1 línea** del `workspace.dsl` (la definición del contenedor) y se vuelve a
exportar. Los identificadores (`eco.cola`) no cambian, por lo que las relaciones no se tocan.

### Conclusión

Escribir a mano es adecuado para un único diagrama de ejemplo o para explorar notación; para un sistema con
cinco vistas que deben mantenerse coherentes con los ADR y con el Laboratorio 05, el modelo único reduce el
trabajo de mantenimiento y los errores de divergencia, a costa de depender de la herramienta y de un paso de
post-proceso para los externos.
