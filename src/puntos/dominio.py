from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class CuentaPuntos:
    vecino_id: UUID
    saldo: int = 0
    id: UUID = field(default_factory=uuid4)
    acreditadas: set[UUID] = field(default_factory=set, repr=False)

    def acreditar(self, puntos: int, solicitud_id: UUID) -> None:
        if puntos < 0:
            raise ValueError("Los puntos no pueden ser negativos")
        if solicitud_id in self.acreditadas:  # idempotencia
            return
        self.acreditadas.add(solicitud_id)
        self.saldo += puntos
