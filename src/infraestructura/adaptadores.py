from __future__ import annotations

from uuid import UUID

from solicitudes.dominio import Solicitud
from solicitudes.puertos import Notificador, RepositorioSolicitudes


class NotificadorAdapter(Notificador):
    def notificar_asignacion(self, s: Solicitud) -> None:
        raise NotImplementedError("Integrar con el proveedor de notificaciones")

    def notificar_puntos(self, s: Solicitud, puntos: int) -> None:
        raise NotImplementedError("Integrar con el proveedor de notificaciones")


class RepositorioSolicitudesORM(RepositorioSolicitudes):
    def buscar(self, id: UUID) -> Solicitud:
        raise NotImplementedError("Implementar con el ORM de Django")

    def guardar(self, s: Solicitud) -> None:
        raise NotImplementedError("Implementar con el ORM de Django")

    def listar_por_reciclador(self, reciclador_id: UUID) -> list[Solicitud]:
        raise NotImplementedError("Implementar con el ORM de Django")
