"""Dominio del módulo solicitudes: Vecino, Solicitud, ItemMaterial y EstadoSolicitud."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from compartido.tipos import Pesaje, TipoMaterial


class TransicionInvalida(Exception):
    """Se intentó una transición no permitida por la máquina de estados (regla C2)."""


class EstadoSolicitud(Enum):
    PENDIENTE = "PENDIENTE"
    ASIGNADA = "ASIGNADA"
    RECOGIDA = "RECOGIDA"
    PESADA = "PESADA"
    PUNTOS_ACREDITADOS = "PUNTOS_ACREDITADOS"
    CANCELADA = "CANCELADA"


@dataclass
class Vecino:
    id: UUID
    nombre: str
    celular: str  # único dato de contacto; Ley N.º 29733: solo para notificar


@dataclass
class ItemMaterial:
    tipo: TipoMaterial
    peso_estimado_kg: Decimal
    peso_real_kg: Decimal | None = None

    def registrar_peso_real(self, kg: Decimal) -> None:
        if kg <= 0:
            raise ValueError("El peso real debe ser mayor que cero")
        self.peso_real_kg = kg


@dataclass
class Solicitud:
    vecino_id: UUID
    distrito_id: UUID
    direccion: str
    latitud: Decimal
    longitud: Decimal
    franja_horaria: str
    id: UUID = field(default_factory=uuid4)
    fecha_registro: datetime = field(default_factory=datetime.now)
    estado: EstadoSolicitud = EstadoSolicitud.PENDIENTE
    reciclador_id: UUID | None = None
    items: list[ItemMaterial] = field(default_factory=list)
    motivo_cancelacion: str | None = None

    # -- helpers -----------------------------------------------------------
    def _exigir(self, *permitidos: EstadoSolicitud, operacion: str) -> None:
        if self.estado not in permitidos:
            raise TransicionInvalida(
                f"{operacion}() no es válida desde el estado {self.estado.value}"
            )

    # -- operaciones del diagrama de clases --------------------------------
    def agregar_material(self, tipo: TipoMaterial, peso_estimado_kg: Decimal) -> None:
        self._exigir(EstadoSolicitud.PENDIENTE, operacion="agregar_material")
        if peso_estimado_kg <= 0:
            raise ValueError("El peso estimado debe ser mayor que cero")
        self.items.append(ItemMaterial(tipo, peso_estimado_kg))

    def asignar(self, reciclador_id: UUID) -> None:
        """PENDIENTE -> ASIGNADA."""
        self._exigir(EstadoSolicitud.PENDIENTE, operacion="asignar")
        self.reciclador_id = reciclador_id
        self.estado = EstadoSolicitud.ASIGNADA

    def liberar(self) -> None:
        """ASIGNADA -> PENDIENTE (visita sin recojo: 'no recolectada')."""
        self._exigir(EstadoSolicitud.ASIGNADA, operacion="liberar")
        self.reciclador_id = None
        self.estado = EstadoSolicitud.PENDIENTE

    def confirmar_recojo(self) -> None:
        """ASIGNADA -> RECOGIDA."""
        self._exigir(EstadoSolicitud.ASIGNADA, operacion="confirmar_recojo")
        self.estado = EstadoSolicitud.RECOGIDA

    def registrar_pesaje(self, pesajes: list[Pesaje]) -> None:
        """RECOGIDA -> PESADA [pesaje con al menos un material]."""
        self._exigir(EstadoSolicitud.RECOGIDA, operacion="registrar_pesaje")
        if not pesajes:
            raise ValueError("El pesaje debe incluir al menos un material")
        for p in pesajes:
            item = next((i for i in self.items if i.tipo == p.tipo), None)
            if item is None:  # el vecino entregó un material no declarado
                item = ItemMaterial(p.tipo, p.kg)
                self.items.append(item)
            item.registrar_peso_real(p.kg)
        self.estado = EstadoSolicitud.PESADA

    def marcar_puntos_acreditados(self) -> None:
        """PESADA -> PUNTOS_ACREDITADOS."""
        self._exigir(EstadoSolicitud.PESADA, operacion="marcar_puntos_acreditados")
        self.estado = EstadoSolicitud.PUNTOS_ACREDITADOS

    def cancelar(self, motivo: str) -> None:
        """PENDIENTE | ASIGNADA -> CANCELADA."""
        self._exigir(EstadoSolicitud.PENDIENTE, EstadoSolicitud.ASIGNADA, operacion="cancelar")
        self.motivo_cancelacion = motivo
        self.estado = EstadoSolicitud.CANCELADA

    def peso_total_real(self) -> Decimal:
        return sum((i.peso_real_kg or Decimal(0) for i in self.items), Decimal(0))

    def pesajes_reales(self) -> list[Pesaje]:
        return [Pesaje(i.tipo, i.peso_real_kg) for i in self.items if i.peso_real_kg]
