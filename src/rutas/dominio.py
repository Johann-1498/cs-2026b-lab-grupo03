from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Reciclador:
    id: UUID
    nombre: str
    asociacion: str
    distrito_id: UUID
    disponible: bool = True

    def esta_disponible(self) -> bool:
        return self.disponible
