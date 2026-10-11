from __future__ import annotations

from uuid import UUID

from compartido.tipos import Pesaje

from .dominio import CuentaPuntos
from .reglas import ReglaPuntos


class ServicioPuntos:
    def __init__(self, reglas: list[ReglaPuntos]) -> None:
        if not reglas:
            raise ValueError("Debe existir al menos una regla de puntos")
        self.reglas = reglas
        self.cuentas: dict[UUID, CuentaPuntos] = {}

    def acreditar(
        self, vecino_id: UUID, distrito_id: UUID, solicitud_id: UUID, pesajes: list[Pesaje]
    ) -> int:
        # la regla más específica (la última que aplica) gana
        regla = [r for r in self.reglas if r.aplica_a(distrito_id)][-1]
        puntos = regla.calcular(pesajes)
        cuenta = self.cuentas.setdefault(vecino_id, CuentaPuntos(vecino_id))
        cuenta.acreditar(puntos, solicitud_id)
        return puntos

    def consultar_saldo(self, vecino_id: UUID) -> int:
        cuenta = self.cuentas.get(vecino_id)
        return cuenta.saldo if cuenta else 0
