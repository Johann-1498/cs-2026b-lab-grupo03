"""Una prueba por transición del diagrama de estados (docs/design/estados-solicitud.mmd)."""
from decimal import Decimal
from uuid import uuid4

import pytest

from compartido.tipos import Pesaje, TipoMaterial
from solicitudes.dominio import EstadoSolicitud as E
from solicitudes.dominio import Solicitud, TransicionInvalida


def nueva() -> Solicitud:
    s = Solicitud(uuid4(), uuid4(), "Av. Ejemplo 123", Decimal("-16.4"), Decimal("-71.5"), "08:00-10:00")
    s.agregar_material(TipoMaterial.PLASTICO, Decimal("3"))
    return s


def asignada() -> Solicitud:
    s = nueva()
    s.asignar(uuid4())
    return s


def pesada() -> Solicitud:
    s = asignada()
    s.confirmar_recojo()
    s.registrar_pesaje([Pesaje(TipoMaterial.PLASTICO, Decimal("2.5"))])
    return s


def test_T1_inicial_pendiente():
    assert nueva().estado is E.PENDIENTE


def test_T2_pendiente_a_asignada():
    s = nueva(); s.asignar(uuid4())
    assert s.estado is E.ASIGNADA and s.reciclador_id is not None


def test_T3_pendiente_a_cancelada():
    s = nueva(); s.cancelar("el vecino ya no la requiere")
    assert s.estado is E.CANCELADA


def test_T4_asignada_a_recogida():
    s = asignada(); s.confirmar_recojo()
    assert s.estado is E.RECOGIDA


def test_T5_asignada_a_pendiente_no_recolectada():
    s = asignada(); s.liberar()
    assert s.estado is E.PENDIENTE and s.reciclador_id is None


def test_T6_asignada_a_cancelada():
    s = asignada(); s.cancelar("vecino ausente")
    assert s.estado is E.CANCELADA


def test_T7_recogida_a_pesada():
    s = pesada()
    assert s.estado is E.PESADA and s.peso_total_real() == Decimal("2.5")


def test_T8_pesada_a_puntos_acreditados():
    s = pesada(); s.marcar_puntos_acreditados()
    assert s.estado is E.PUNTOS_ACREDITADOS


# --- guardas y transiciones prohibidas (C2) ---------------------------------
def test_G1_pesaje_vacio_no_permite_pesar():
    s = asignada(); s.confirmar_recojo()
    with pytest.raises(ValueError):
        s.registrar_pesaje([])
    assert s.estado is E.RECOGIDA


@pytest.mark.parametrize("op", ["asignar", "confirmar_recojo", "liberar"])
def test_G2_estados_finales_no_tienen_salida(op):
    s = pesada(); s.marcar_puntos_acreditados()
    with pytest.raises(TransicionInvalida):
        getattr(s, op)(*([uuid4()] if op == "asignar" else []))


def test_G3_no_se_cancela_una_solicitud_ya_recogida():
    s = asignada(); s.confirmar_recojo()
    with pytest.raises(TransicionInvalida):
        s.cancelar("tarde")


def test_G4_no_se_pesa_sin_recoger():
    s = asignada()
    with pytest.raises(TransicionInvalida):
        s.registrar_pesaje([Pesaje(TipoMaterial.VIDRIO, Decimal("1"))])


@pytest.mark.parametrize("op", ["asignar", "confirmar_recojo", "liberar", "cancelar"])
def test_G5_cancelada_es_estado_final(op):
    s = nueva(); s.cancelar("prueba")
    with pytest.raises(TransicionInvalida):
        getattr(s, op)(*([uuid4()] if op == "asignar" else ["otra"] if op == "cancelar" else []))
