workspace "EcoRecicla AQP" "Modelo C4 de la plataforma de recojo domiciliario de reciclables de Arequipa (MVP en 1 mes)." {

    !identifiers hierarchical

    model {
        vecino = person "Vecino" "Solicita el recojo de sus reciclables y acumula puntos ecológicos."
        reciclador = person "Reciclador" "Reciclador formalizado: recorre su ruta diaria, recoge y pesa el material."
        municipalidad = person "Administrador municipal" "Gestiona distritos y asociaciones de recicladores y consulta reportes de toneladas."

        eco = softwareSystem "EcoRecicla AQP" "Permite solicitar el recojo de reciclables, asignar recicladores, registrar el pesaje, acreditar puntos y reportar toneladas." {

            webCiudadana = container "Aplicación web de vecinos y municipalidad" "Interfaz para solicitar recojos, consultar puntos, gestionar distritos y descargar reportes." "Aplicación web (navegador)" "Web Browser"
            pwaReciclador = container "PWA del reciclador" "Ruta del día y registro de recojo y pesaje en 4 toques o menos; guarda los registros en el celular si no hay señal 3G." "Progressive Web App (Service Worker)" "Mobile App"

            api = container "API EcoRecicla" "Monolito modular que implementa los casos de uso mediante una API REST con autenticación JWT (ADR-001, ADR-003)." "Python / Django REST Framework / simplejwt" {
                solicitudes = component "Módulo Solicitudes" "Registra solicitudes de recojo y gestiona su ciclo de vida (PENDIENTE a PUNTOS_ACREDITADOS)." "Django app"
                rutas = component "Módulo Rutas" "Asigna recicladores (realiza el puerto AsignadorReciclador) y genera la ruta del día." "Django app"
                distritos = component "Módulo Distritos" "Gestiona distritos, sectores de cobertura y asociaciones de recicladores." "Django app"
                puntos = component "Módulo Puntos" "Calcula y acredita puntos con una regla por distrito (patrón Strategy)." "Django app"
                reportes = component "Módulo Reportes" "Reportes consolidados de toneladas por distrito, material, reciclador y fechas." "Django app"
                compartido = component "Núcleo compartido" "Tipos de valor comunes: TipoMaterial y Pesaje." "Paquete Python"
                infraestructura = component "Adaptadores de infraestructura" "Implementan los puertos: repositorio de solicitudes (ORM), notificador e incentivos." "Paquete Python / Django ORM"
            }

            worker = container "Worker de tareas" "Ejecuta de forma asíncrona los reportes y el envío de notificaciones, con reintentos." "Celery"
            db = container "Base de datos" "Solicitudes, rutas, puntos, distritos y reportes (esquemas modulares, ADR-002)." "PostgreSQL" "Database"
            cola = container "Cola y caché" "Cola de tareas del worker y caché de consultas." "Redis" "Queue"
        }

        notificaciones = softwareSystem "Servicio de notificaciones" "Entrega avisos de asignación y de puntos a vecinos y recicladores." "Externo,External"
        incentivos = softwareSystem "Sistema de incentivos municipales" "Gestiona los beneficios que los vecinos canjean con sus puntos." "Externo,External"

        # --- Nivel 1: contexto ------------------------------------------------
        vecino -> eco "Solicita recojos y consulta sus puntos"
        reciclador -> eco "Consulta su ruta y registra recojos y pesajes"
        municipalidad -> eco "Gestiona distritos y descarga reportes"
        eco -> notificaciones "Envía avisos de asignación y de puntos" "HTTPS/JSON"
        eco -> incentivos "Registra el canje de puntos" "HTTPS/JSON"

        # --- Nivel 2: contenedores -------------------------------------------
        vecino -> eco.webCiudadana "Solicita recojos y consulta sus puntos" "HTTPS"
        municipalidad -> eco.webCiudadana "Gestiona distritos y descarga reportes" "HTTPS"
        reciclador -> eco.pwaReciclador "Consulta su ruta y registra recojos, con o sin conexión" "HTTPS"
        eco.webCiudadana -> eco.api "Llama a" "HTTPS/JSON (REST + JWT)" "ViaProxy"
        eco.pwaReciclador -> eco.api "Consulta rutas y envía pesajes" "HTTPS/JSON (REST + JWT)" "ViaProxy"
        eco.api -> eco.db "Lee y escribe" "SQL/TCP"
        eco.api -> eco.cola "Encola tareas y lee caché" "Redis protocol"
        eco.worker -> eco.cola "Consume tareas" "Redis protocol"
        eco.worker -> eco.db "Lee datos y guarda reportes" "SQL/TCP"
        eco.worker -> notificaciones "Envía mensajes" "HTTPS/JSON"
        eco.api -> incentivos "Registra canjes de puntos" "HTTPS/JSON"

        # --- Nivel 3: componentes de la API -----------------------------------
        eco.webCiudadana -> eco.api.solicitudes "Registra y consulta solicitudes" "HTTPS/JSON"
        eco.webCiudadana -> eco.api.puntos "Consulta su saldo de puntos" "HTTPS/JSON"
        eco.webCiudadana -> eco.api.distritos "Gestiona distritos y cobertura" "HTTPS/JSON"
        eco.webCiudadana -> eco.api.reportes "Descarga reportes" "HTTPS/JSON"
        eco.pwaReciclador -> eco.api.rutas "Consulta la ruta del día" "HTTPS/JSON"
        eco.pwaReciclador -> eco.api.solicitudes "Registra recojo y pesaje" "HTTPS/JSON"

        eco.api.solicitudes -> eco.api.distritos "Verifica la cobertura del distrito"
        eco.api.solicitudes -> eco.api.rutas "Pide asignar un reciclador (puerto AsignadorReciclador)"
        eco.api.solicitudes -> eco.api.puntos "Acredita los puntos del pesaje"
        eco.api.solicitudes -> eco.api.compartido "Usa TipoMaterial y Pesaje"
        eco.api.puntos -> eco.api.compartido "Usa Pesaje"
        eco.api.solicitudes -> eco.api.infraestructura "Guarda y busca solicitudes (puerto RepositorioSolicitudes)"
        eco.api.solicitudes -> eco.api.infraestructura "Pide notificar (puerto Notificador)"
        eco.api.rutas -> eco.api.infraestructura "Lee las solicitudes asignadas (puerto RepositorioSolicitudes)"
        eco.api.reportes -> eco.api.solicitudes "Lee solicitudes (solo lectura)"
        eco.api.reportes -> eco.api.rutas "Lee recicladores y rutas (solo lectura)"
        eco.api.reportes -> eco.api.puntos "Lee puntos (solo lectura)"
        eco.api.reportes -> eco.api.distritos "Lee distritos (solo lectura)"

        eco.api.reportes -> eco.cola "Encola la generación del reporte" "Redis protocol"
        eco.api.rutas -> eco.db "Lee y escribe sus tablas" "SQL/TCP"
        eco.api.distritos -> eco.db "Lee y escribe sus tablas" "SQL/TCP"
        eco.api.puntos -> eco.db "Lee y escribe sus tablas" "SQL/TCP"
        eco.api.infraestructura -> eco.db "Lee y escribe las solicitudes" "SQL/TCP"
        eco.api.infraestructura -> eco.cola "Encola las notificaciones (asíncrono)" "Redis protocol"
        eco.api.infraestructura -> incentivos "Registra canjes de puntos" "HTTPS/JSON"

        # --- Despliegue (despliegue.py del Laboratorio 04, R-03) ---------------
        produccion = deploymentEnvironment "Producción" {
            nav = deploymentNode "Navegador del vecino o de la municipalidad" "" "Navegador web (PC o celular)" {
                webInst = containerInstance eco.webCiudadana
            }
            cel = deploymentNode "Celular del reciclador" "" "Android de gama de entrada, 3G" {
                pwaInst = containerInstance eco.pwaReciclador
            }
            vps = deploymentNode "VPS" "Servidor privado virtual básico (R-03)" "Linux, 2 vCPU, 4 GB RAM" {
                nginx = infrastructureNode "Nginx" "Proxy inverso y terminación HTTPS." "Nginx"
                monolito = deploymentNode "Monolito modular" "" "Python / Django" {
                    apiInst = containerInstance eco.api
                    workerInst = containerInstance eco.worker
                    colaInst = containerInstance eco.cola
                }
                servidordb = deploymentNode "Servidor de base de datos" "" "PostgreSQL" {
                    dbInst = containerInstance eco.db
                }
                monitoreo = infrastructureNode "Monitoreo" "Métricas y registros del VPS." "Prometheus / logs"
            }

            nav.webInst -> vps.nginx "Llama a" "HTTPS/JSON"
            cel.pwaInst -> vps.nginx "Llama a" "HTTPS/JSON"
            vps.nginx -> vps.monolito.apiInst "Reenvía las peticiones" "HTTP"
            vps.monolito.apiInst -> vps.monitoreo "Envía métricas y registros" "HTTP"
        }
    }

    views {
        systemContext eco "Contexto" "Nivel 1: EcoRecicla AQP y su entorno." {
            include *
            autolayout lr
        }
        container eco "Contenedores" "Nivel 2: contenedores de EcoRecicla AQP." {
            include *
            autolayout lr
        }
        component eco.api "Componentes" "Nivel 3: módulos de la API (coinciden con docs/design/paquetes.puml)." {
            include *
            autolayout lr
        }
        dynamic eco.api "SolicitarRecojo" "Dinámico: solicitar el recojo de reciclables (HU-03)." {
            eco.webCiudadana -> eco.api.solicitudes "POST /api/solicitudes"
            eco.api.solicitudes -> eco.api.distritos "Verifica la cobertura"
            eco.api.solicitudes -> eco.api.infraestructura "Guarda la solicitud (PENDIENTE)"
            eco.api.solicitudes -> eco.api.rutas "Pide asignar un reciclador"
            eco.api.solicitudes -> eco.api.infraestructura "Guarda la asignación (ASIGNADA)"
            eco.api.infraestructura -> eco.cola "Encola la notificación (asíncrono)"
            eco.worker -> eco.cola "Toma la tarea de notificación"
            eco.worker -> notificaciones "Envía el aviso de asignación"
            autolayout lr
        }
        deployment eco produccion "Despliegue" "Despliegue en producción (MVP en un único VPS)." {
            include *
            exclude "relationship.tag==ViaProxy"
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
            element "Mobile App" {
                shape MobileDevicePortrait
            }
        }
    }
}
