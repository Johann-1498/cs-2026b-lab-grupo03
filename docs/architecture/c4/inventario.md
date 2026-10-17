# Inventario de elementos del modelo C4 – EcoRecicla AQP

Cada elemento de `workspace.dsl` proviene de un artefacto de los Laboratorios 04 y 05 (Tabla 6 de la guía).

## 1. Personas, sistemas y contenedores

| Elemento | Tipo C4 | Origen |
|---|---|---|
| Vecino | Persona | `drivers.md` (RF-01, RF-04) |
| Reciclador | Persona | `drivers.md` (RF-02, RF-03); `despliegue.py` (PWA Reciclador, celular 3G) |
| Administrador municipal | Persona | `drivers.md` (Municipalidad: RF-05, RF-06); `adr/003-autenticacion.md` (Administradores Municipales) |
| EcoRecicla AQP | Sistema de software | README del Lab 04 (caso 10) |
| Servicio de notificaciones | Sistema externo | `diagramas/arquitectura.mmd` (Servicios externos: Notificaciones); puerto `Notificador` (Lab 05) |
| Sistema de incentivos municipales | Sistema externo | `diagramas/arquitectura.mmd` (Incentivos); RF-04 (canje de puntos) |
| Aplicación web de vecinos y municipalidad | Contenedor | `despliegue.py` (Vecinos y Municipalidad); ADR-001 (capa de presentación) |
| PWA del reciclador | Contenedor | `despliegue.py` (PWA Reciclador); QA-02 y fiabilidad (3G inestable) |
| API EcoRecicla | Contenedor | `adr/001` (monolito modular Django); `adr/003` (JWT con simplejwt) |
| Worker de tareas | Contenedor | `despliegue.py` (Celery Worker, reportes asíncronos); nota "asíncrono" de la secuencia del Lab 05 |
| Base de datos | Contenedor | `adr/002` (PostgreSQL con esquemas modulares) |
| Cola y caché | Contenedor | `despliegue.py` (Redis, caché y broker) |

## 2. Componentes de la API (nivel 3)

| Componente | Tipo C4 | Origen |
|---|---|---|
| Módulo Solicitudes | Componente | paquete `solicitudes` de `docs/design/paquetes.puml` (Lab 05) |
| Módulo Rutas | Componente | paquete `rutas` (realiza `AsignadorReciclador`, ADR-004) |
| Módulo Distritos | Componente | paquete `distritos` |
| Módulo Puntos | Componente | paquete `puntos` (Strategy, QA-01) |
| Módulo Reportes | Componente | paquete `reportes` |
| Núcleo compartido | Componente | paquete `compartido` (`TipoMaterial`, `Pesaje`) |
| Adaptadores de infraestructura | Componente | paquete `infraestructura` (`NotificadorAdapter`, `RepositorioSolicitudesORM`) |

## 3. Vistas y niveles

| Vista | Origen |
|---|---|
| Nivel 4 (código) | No se redibuja: se enlaza `docs/design/clases.puml` (Lab 05) |
| Dinámica "Solicitar recojo" | `docs/design/secuencia-solicitar-recojo.puml` (Lab 05) |
| Despliegue "Producción" | `despliegue.py` (Lab 04) y restricción R-03 (VPS de 2 vCPU y 4 GB RAM) |

## 4. Infraestructura que NO es contenedor C4

| Elemento | Dónde se modela | Origen |
|---|---|---|
| VPS (2 vCPU, 4 GB RAM) | Nodo de despliegue | R-03; `despliegue.py` |
| Nginx (proxy inverso y HTTPS) | Nodo de infraestructura | `despliegue.py` |
| Monitoreo (Prometheus / logs) | Nodo de infraestructura | `despliegue.py` |

## 5. Decisiones y supuestos del modelo

| # | Decisión / supuesto | Justificación |
|---|---|---|
| 1 | No se modela Docker ni Docker Compose. | No figura en ADR-001 ni en `despliegue.py`; solo se usan tecnologías de esos artefactos. |
| 2 | No se modela un "servicio de mapas" (sugerido en la Tabla 10 de la guía). | No existe en los ADR ni en el diseño del Lab 05: las coordenadas se guardan, pero la ruta se ordena por franja horaria. |
| 3 | El `Notificador` asíncrono se implementa encolando una tarea en Redis que ejecuta el worker. | La secuencia del Lab 05 lo marca como asíncrono ("no bloquea la respuesta"); Celery y Redis ya están en `despliegue.py`. |
| 4 | Las flechas de C4 indican **uso en ejecución**; las del diagrama de paquetes, **dependencia de compilación**. | Con puertos, ambos sentidos pueden diferir (ver ADR-004); el verificador `verificar_c4.py` formaliza la correspondencia. |
| 5 | No se fija la versión de PostgreSQL ni el sistema operativo del VPS (solo "Linux"). | El ADR-002 y `drivers.md` no las definen; se fijarán al aprovisionar el VPS. |
| 6 | El canje de puntos (RF-04) aparece como relación hacia el sistema de incentivos. | Está en `arquitectura.mmd` y en `drivers.md`; su adaptador queda fuera de HU-03 y se diseñará después. |
