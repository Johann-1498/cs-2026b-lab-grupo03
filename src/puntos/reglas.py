"""Estrategias de cálculo de puntos (ADR-001: patrón Strategy para QA-01)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from compartido.tipos import Pesaje, TipoMaterial


class ReglaPuntos(ABC):
    @abstractmethod
    def aplica_a(self, distrito_id: UUID) -> bool: ...

    @abstractmethod
    def calcular(self, pesajes: list[Pesaje]) -> int: ...


class ReglaPuntosPorKg(ReglaPuntos):
    # Supuesto del equipo: valores de ejemplo; se configuran por distrito.
    POR_DEFECTO = {
        TipoMaterial.PLASTICO: 10,
        TipoMaterial.PAPEL_CARTON: 5,
        TipoMaterial.VIDRIO: 4,
        TipoMaterial.METAL: 12,
    }

    def __init__(self, distrito_id: UUID | None = None, puntos_por_kg: dict | None = None):
        self.distrito_id = distrito_id  # None = regla general
        self.puntos_por_kg = puntos_por_kg or dict(self.POR_DEFECTO)

    def aplica_a(self, distrito_id: UUID) -> bool:
        return self.distrito_id is None or self.distrito_id == distrito_id

    def calcular(self, pesajes: list[Pesaje]) -> int:
        total = sum((p.kg * self.puntos_por_kg[p.tipo] for p in pesajes), Decimal(0))
        return int(total)
