from __future__ import annotations

from uuid import UUID

from .dominio import Distrito


class ServicioDistritos:
    def __init__(self, distritos: list[Distrito]) -> None:
        self._distritos = {d.id: d for d in distritos}

    def verificar_cobertura(self, distrito_id: UUID) -> bool:
        d = self._distritos.get(distrito_id)
        return d is not None and d.tiene_cobertura()
