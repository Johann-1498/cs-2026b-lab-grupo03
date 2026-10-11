"""Criterios de aceptación de HU-03 (docs/design/historia.md)."""
from decimal import Decimal
from uuid import uuid4

import pytest

from compartido.tipos import Pesaje, TipoMaterial
from distritos.dominio import Distrito
from distritos.services import ServicioDistritos
from puntos.reglas import ReglaPuntosPorKg
from puntos.services import ServicioPuntos
from rutas.dominio import Reciclador
from rutas.services import ServicioRutas
from solicitudes.dominio import EstadoSolicitud as E
from solicitudes.services import ServicioSolicitudes, SolicitudInvalida

from fakes import NotificadorEspia, RepoMemoria

CAYMA, SIN_COBERTURA = uuid4(), uuid4()
MATERIALES = [Pesaje(TipoMaterial.PLASTICO, Decimal("3")), Pesaje(TipoMaterial.VIDRIO, Decimal("2"))]


def armar(recicladores=None, reglas=None):
    repo, notif = RepoMemoria(), NotificadorEspia()
    rutas = ServicioRutas(
        recicladores if recicladores is not None else [Reciclador(uuid4(), "Rosa", "Asoc. Verde", CAYMA)],
        repo,
    )
    distritos = ServicioDistritos([Distrito(CAYMA, "Cayma"), Distrito(SIN_COBERTURA, "Otro", activo=False)])
    puntos = ServicioPuntos(reglas or [ReglaPuntosPorKg()])
    return ServicioSolicitudes(repo, notif, rutas, distritos, puntos), repo, notif, puntos


def test_CA1_solicitud_valida_queda_asignada_y_se_notifica():
    svc, repo, notif, _ = armar()
    s = svc.solicitar_recojo(uuid4(), CAYMA, "Calle 1", "08:00-10:00", MATERIALES)
    assert s.estado is E.ASIGNADA and s.reciclador_id is not None
    assert len(s.items) == 2 and notif.asignaciones == [s]


def test_CA1b_sin_reciclador_disponible_queda_pendiente_sin_notificar():
    svc, _, notif, _ = armar(recicladores=[])
    s = svc.solicitar_recojo(uuid4(), CAYMA, "Calle 1", "08:00-10:00", MATERIALES)
    assert s.estado is E.PENDIENTE and notif.asignaciones == []


def test_CA2_distrito_sin_cobertura_no_crea_solicitud():
    svc, repo, _, _ = armar()
    with pytest.raises(SolicitudInvalida):
        svc.solicitar_recojo(uuid4(), SIN_COBERTURA, "Calle 1", "08:00-10:00", MATERIALES)
    assert repo.datos == {}


def test_CA2b_sin_materiales_no_crea_solicitud():
    svc, repo, _, _ = armar()
    with pytest.raises(SolicitudInvalida):
        svc.solicitar_recojo(uuid4(), CAYMA, "Calle 1", "08:00-10:00", [])
    assert repo.datos == {}


def test_CA3_confirmar_recojo_acredita_puntos_segun_regla():
    svc, repo, notif, puntos = armar()
    vecino = uuid4()
    s = svc.solicitar_recojo(vecino, CAYMA, "Calle 1", "08:00-10:00", MATERIALES)
    svc.registrar_recojo(s.id, [Pesaje(TipoMaterial.PLASTICO, Decimal("2.5")), Pesaje(TipoMaterial.VIDRIO, Decimal("2"))])
    # 2.5 kg * 10 + 2 kg * 4 = 33
    assert repo.buscar(s.id).estado is E.PUNTOS_ACREDITADOS
    assert puntos.consultar_saldo(vecino) == 33 and notif.puntos[0][1] == 33


def test_QA01_nueva_regla_por_distrito_sin_tocar_otros_modulos():
    """Modificabilidad: Cayma duplica los puntos agregando UNA clase/instancia de ReglaPuntos."""
    doble = {k: v * 2 for k, v in ReglaPuntosPorKg.POR_DEFECTO.items()}
    svc, repo, _, puntos = armar(reglas=[ReglaPuntosPorKg(), ReglaPuntosPorKg(CAYMA, doble)])
    vecino = uuid4()
    s = svc.solicitar_recojo(vecino, CAYMA, "Calle 1", "08:00-10:00", MATERIALES)
    svc.registrar_recojo(s.id, [Pesaje(TipoMaterial.PLASTICO, Decimal("1"))])
    assert puntos.consultar_saldo(vecino) == 20


def test_ruta_del_dia_ordenada_por_franja():
    from datetime import date
    rec = Reciclador(uuid4(), "Rosa", "Asoc. Verde", CAYMA)
    svc, repo, _, _ = armar(recicladores=[rec])
    a = svc.solicitar_recojo(uuid4(), CAYMA, "A", "10:00-12:00", MATERIALES)
    b = svc.solicitar_recojo(uuid4(), CAYMA, "B", "08:00-10:00", MATERIALES)
    ruta = ServicioRutas([rec], repo).generar_ruta_del_dia(rec.id, date.today())
    assert [p.direccion for p in ruta] == ["B", "A"]
