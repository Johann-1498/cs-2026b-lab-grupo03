"""Dobles de prueba para los puertos (no son parte del diseño; solo de las pruebas)."""
from uuid import UUID

from solicitudes.dominio import Solicitud
from solicitudes.puertos import Notificador, RepositorioSolicitudes


class RepoMemoria(RepositorioSolicitudes):
    def __init__(self):
        self.datos: dict[UUID, Solicitud] = {}
        self.guardados = 0

    def buscar(self, id):
        return self.datos[id]

    def guardar(self, s):
        self.datos[s.id] = s
        self.guardados += 1

    def listar_por_reciclador(self, reciclador_id):
        return [s for s in self.datos.values() if s.reciclador_id == reciclador_id]


class NotificadorEspia(Notificador):
    def __init__(self):
        self.asignaciones: list[Solicitud] = []
        self.puntos: list[tuple[Solicitud, int]] = []

    def notificar_asignacion(self, s):
        self.asignaciones.append(s)

    def notificar_puntos(self, s, puntos):
        self.puntos.append((s, puntos))
