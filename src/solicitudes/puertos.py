"""Puertos (interfaces) del módulo solicitudes (ADR-001, ADR-004)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from .dominio import Solicitud


class RepositorioSolicitudes(ABC):
    @abstractmethod
    def buscar(self, id: UUID) -> Solicitud: ...

    @abstractmethod
    def guardar(self, s: Solicitud) -> None: ...

    @abstractmethod
    def listar_por_reciclador(self, reciclador_id: UUID) -> list[Solicitud]: ...


class Notificador(ABC):
    """Puerto hacia el servicio externo de notificaciones."""

    @abstractmethod
    def notificar_asignacion(self, s: Solicitud) -> None: ...

    @abstractmethod
    def notificar_puntos(self, s: Solicitud, puntos: int) -> None: ...


class AsignadorReciclador(ABC):
    """Puerto que invierte la dependencia solicitudes <-> rutas (ADR-004)."""

    @abstractmethod
    def asignar(self, s: Solicitud) -> UUID | None:
        """Devuelve el id del reciclador asignado o None si no hay disponible."""
