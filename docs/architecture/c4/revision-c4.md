# Revisión de las cinco vistas con la lista oficial de c4model.com – EcoRecicla AQP

Lista aplicada: Tabla 3 de la guía (resumen de c4model.com/diagrams/checklist). Evidencias: PNG en `img/` y
verificador automático `scripts/verificar_c4.py`.

## 1. Lista de revisión por vista

| Vista | General (título, alcance, leyenda) | Elementos (nombre, tipo, descripción, tecnología) | Relaciones (etiqueta, protocolo, estilos) |
|---|---|---|---|
| **Contexto** (nivel 1) | **Sí.** Título "System Context View: EcoRecicla AQP" + descripción "Nivel 1…"; leyenda con persona, sistema y sistema externo. | **Sí.** 3 personas, 1 sistema y 2 externos (gris) con descripción; sin tecnologías internas. | **Sí.** Cada flecha tiene un verbo de intención ("Solicita recojos…", "Envía avisos…"); los sistemas externos indican `HTTPS/JSON`. |
| **Contenedores** (nivel 2) | **Sí.** Título, descripción y leyenda (persona, contenedor, sistema externo, límite). | **Sí.** 6 contenedores con descripción y tecnología entre corchetes (`Celery`, `PostgreSQL`, `Redis`…). **Parcial:** la base de datos y la cola se dibujan como cajas; solo la tecnología las distingue. | **Sí.** Todas las flechas con etiqueta y protocolo (`HTTPS/JSON (REST + JWT)`, `SQL/TCP`, `Redis protocol`). |
| **Componentes** (nivel 3) | **Sí.** Título "Component View: … API EcoRecicla", descripción y leyenda. | **Sí.** 7 componentes con tecnología (`Django app`, `Paquete Python`) y responsabilidad. | **Sí.** Etiquetas con la intención y, cuando hay puerto, su nombre. **Parcial:** la densidad de flechas hace que algunas etiquetas toquen el borde del límite de la API. |
| **Dinámica** "Solicitar recojo" | **Sí.** Título, descripción y leyenda. | **Sí.** Mismos elementos que la vista de componentes. | **Sí.** 8 pasos numerados; cada paso corresponde a una relación existente del modelo (verificado automáticamente). |
| **Despliegue** "Producción" | **Sí.** Título, entorno y descripción; leyenda de contenedor y nodo. | **Sí.** Nodos anidados con sistema operativo y tamaño ("Linux, 2 vCPU, 4 GB RAM"); instancia de **cada** contenedor. | **Sí.** Protocolos `HTTPS/JSON`, `HTTP`, `SQL/TCP`. **Parcial:** la etiqueta "Envía métricas y registros" se solapa con el título del nodo "Monolito modular" (limitación del autolayout). |

## 2. Revisión cruzada con IA (Prompt IA 2 – auditor C4)

| # | Vista | Hallazgo de la IA | Verificación del equipo | Decisión |
|---|---|---|---|---|
| 1 | Contenedores | Las flechas persona → contenedor dicen solo "Usa"; no describen la intención. | **Correcto.** Incumplía la lista de verificación de E1 ("Solicita cobros", no "usa"). | **Corregido:** "Solicita recojos y consulta sus puntos", "Gestiona distritos y descarga reportes", "Consulta su ruta y registra recojos, con o sin conexión". El verificador ahora rechaza esas etiquetas vagas. |
| 2 | Dinámica / Componentes | El paso 4 `Solicitudes → Rutas` contradice `paquetes.puml` (donde `rutas` depende de `solicitudes`) y forma un ciclo. | **Falso positivo.** C4 muestra el **uso en ejecución**; con el puerto `AsignadorReciclador` (ADR-004) la dependencia de compilación del Lab 05 va en sentido contrario. El modelo es acíclico (`verificar_c4.py`, E3). | Rechazado |
| 3 | Componentes | La PWA, la web, la cola y la base de datos aparecen fuera del límite de la API: "error de alcance". | **Falso positivo.** Una vista de componentes muestra los contenedores vecinos con los que interactúan los componentes; es la convención de C4. | Rechazado |
| 4 | Contenedores | La flecha "Encola tareas y lee caché" mezcla dos intenciones. | **Correcto parcialmente.** Ambas usan el mismo protocolo y contenedor (Redis); se aceptan y la descripción del contenedor lo documenta. | Aceptado |
| 5 | Componentes | "Núcleo compartido" y "Adaptadores de infraestructura" no son módulos del ADR-001 (que lista cinco dominios). | **Correcto parcialmente.** Existen como paquetes en `paquetes.puml` (Lab 05) y como capa de infraestructura en `arquitectura.mmd` (Lab 04): se mantienen para coincidir con el diseño. | Aceptado |
| 6 | Despliegue | No se indica la versión de PostgreSQL ni del sistema operativo. | **Correcto.** El ADR-002 y `drivers.md` no las fijan; queda como supuesto 5 de `inventario.md`. | Aceptado (pendiente al aprovisionar) |
| 7 | Despliegue | La etiqueta de monitoreo se solapa con el título de un nodo. | **Correcto,** es una limitación del autolayout de PlantUML. | Aceptado |
| 8 | Todas | Hay título, descripción y leyenda en las cinco vistas. | **Correcto** (cumple). | — |

**Resumen:** 8 hallazgos → 2 falsos positivos (2 y 3), 1 corrección aplicada (1), 4 aceptados con
justificación (4, 5, 6, 7) y 1 confirmación de cumplimiento (8).

## 3. Resultado del verificador automático

```text
E1 contexto: OK
Lista de revisión (general, elementos, relaciones): OK
E2 contenedores (coherencia con ADR-001): OK
E3 componentes (coherencia con paquetes.puml, sin ciclos): OK
E4 vista dinámica: OK
E5 despliegue (coherente con R-03): OK
3 personas, 2 externos, 6 contenedores, 7 componentes, 41 relaciones, 5 vistas
```

Se comprobó con mutaciones que el verificador falla ante un ciclo entre componentes, una tecnología fuera del
ADR (Kafka) y una relación sin protocolo.

## 4. Contradicciones entre artefactos y su corrección

| Contradicción | Artefacto corregido | Registro |
|---|---|---|
| El primer resultado del verificador marcó `rutas → infraestructura` como "sin equivalente" en `paquetes.puml`. | Ninguno estaba equivocado: C4 es uso en ejecución y UML es dependencia de compilación (ADR-004). Se formalizó la regla de correspondencia por puertos en `verificar_c4.py` y en el supuesto 4 de `inventario.md`. | `bitacora-ia.md`, interacción 4 |
