"""Interfaz pública del módulo rutas. Realiza el puerto AsignadorReciclador (ADR-004)."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from solicitudes.dominio import EstadoSolicitud, Solicitud
from solicitudes.puertos import AsignadorReciclador, RepositorioSolicitudes

from .dominio import Reciclador


class ServicioRutas(AsignadorReciclador):
    def __init__(self, recicladores: list[Reciclador], repo: RepositorioSolicitudes) -> None:
        self._recicladores = recicladores
        self._repo = repo

    def asignar(self, s: Solicitud) -> UUID | None:
        for r in self._recicladores:
            if r.esta_disponible() and r.distrito_id == s.distrito_id:
                return r.id
        return None

    def generar_ruta_del_dia(self, reciclador_id: UUID, fecha: date) -> list[Solicitud]:
        """Paradas ASIGNADAS al reciclador, ordenadas por franja horaria (RF-02)."""
        paradas = [
            s
            for s in self._repo.listar_por_reciclador(reciclador_id)
            if s.estado == EstadoSolicitud.ASIGNADA
        ]
        return sorted(paradas, key=lambda s: s.franja_horaria)
