from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Distrito:
    id: UUID
    nombre: str
    activo: bool = True

    def tiene_cobertura(self) -> bool:
        return self.activo
