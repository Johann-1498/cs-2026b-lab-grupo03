"""Tipos de valor compartidos entre módulos (sin dependencias de otros módulos)."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class TipoMaterial(Enum):
    """Clasificación de residuos reciclables (RF-01)."""

    PLASTICO = "PLASTICO"
    PAPEL_CARTON = "PAPEL_CARTON"
    VIDRIO = "VIDRIO"
    METAL = "METAL"


@dataclass(frozen=True)
class Pesaje:
    """Peso (kg) de un tipo de material. Se usa tanto para lo declarado como para lo pesado."""

    tipo: TipoMaterial
    kg: Decimal

    def __post_init__(self) -> None:
        if self.kg <= 0:
            raise ValueError("El peso debe ser mayor que cero")
