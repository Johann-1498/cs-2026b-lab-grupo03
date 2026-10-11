"""Interfaz pública del módulo solicitudes (ADR-001: los módulos se hablan por services.py)."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from compartido.tipos import Pesaje
from distritos.services import ServicioDistritos
from puntos.services import ServicioPuntos

from .dominio import Solicitud
from .puertos import AsignadorReciclador, Notificador, RepositorioSolicitudes


class SolicitudInvalida(Exception):
    """No se crea la solicitud (criterio de aceptación de error)."""


class ServicioSolicitudes:
    def __init__(
        self,
        repositorio: RepositorioSolicitudes,
        notificador: Notificador,
        asignador: AsignadorReciclador,
        distritos: ServicioDistritos,
        puntos: ServicioPuntos,
    ) -> None:
        self._repo = repositorio
        self._notificador = notificador
        self._asignador = asignador
        self._distritos = distritos
        self._puntos = puntos

    def _materiales_validos(self, materiales: list[Pesaje]) -> bool:
        return len(materiales) >= 1  # regla C3: una solicitud tiene 1..* materiales

    def solicitar_recojo(
        self,
        vecino_id: UUID,
        distrito_id: UUID,
        direccion: str,
        franja: str,
        materiales: list[Pesaje],
        latitud: Decimal = Decimal("0"),
        longitud: Decimal = Decimal("0"),
    ) -> Solicitud:
        if not (
            self._materiales_validos(materiales)
            and self._distritos.verificar_cobertura(distrito_id)
        ):
            raise SolicitudInvalida("Distrito sin cobertura o sin materiales declarados")
        s = Solicitud(vecino_id, distrito_id, direccion, latitud, longitud, franja)
        for m in materiales:
            s.agregar_material(m.tipo, m.kg)
        self._repo.guardar(s)  # queda PENDIENTE
        reciclador_id = self._asignador.asignar(s)
        if reciclador_id is not None:  # opt: hay reciclador disponible
            s.asignar(reciclador_id)
            self._repo.guardar(s)
            self._notificador.notificar_asignacion(s)  # asíncrono en producción
        return s

    def registrar_recojo(self, solicitud_id: UUID, pesajes: list[Pesaje]) -> Solicitud:
        s = self._repo.buscar(solicitud_id)
        s.confirmar_recojo()
        s.registrar_pesaje(pesajes)
        puntos = self._puntos.acreditar(
            s.vecino_id, s.distrito_id, s.id, s.pesajes_reales()
        )
        s.marcar_puntos_acreditados()
        self._repo.guardar(s)
        self._notificador.notificar_puntos(s, puntos)
        return s

    def cancelar_solicitud(self, solicitud_id: UUID, motivo: str) -> Solicitud:
        s = self._repo.buscar(solicitud_id)
        s.cancelar(motivo)
        self._repo.guardar(s)
        return s
