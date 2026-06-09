# src/logistica/gestor_transportes.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core.coordenada import Coordenada
from src.economia.silo import TipoRecurso
from src.logistica.gps import GPS
from src.logistica.transporte import TipoTransporte, Transporte

if TYPE_CHECKING:
    from src.territorio.mapa import Mapa


@dataclass
class EventoLlegada:
    """Evento generado cuando un transporte alcanza su destino."""
    transporte: Transporte
    mensaje: str


@dataclass
class GestorTransportes:
    """
    Registro centralizado de todos los transportes activos en una partida.

    Responsabilidades:
    - Crear transportes con validación de ruta previa
    - Avanzar todos los transportes cada tick
    - Notificar llegadas para transferencia de carga
    - Eliminar transportes completados o cancelados
    """

    # ==========================================
    # ÍNDICES INTERNOS
    # ==========================================
    _por_id: dict[str, Transporte] = field(default_factory=dict)
    _por_posicion: dict[Coordenada, list[str]] = field(default_factory=dict)

    # ==========================================
    # CREACIÓN DE TRANSPORTES
    # ==========================================
    def crear_transporte(
        self,
        mapa: Mapa,
        origen: Coordenada,
        destino: Coordenada,
        tipo: TipoTransporte,
        tipo_recurso: TipoRecurso | None = None,
        cantidad: int = 0,
        velocidad: int = 1,
        propietario_id: str | None = None,
        metadata: dict | None = None,
    ) -> tuple[bool, str, Transporte | None]:
        """
        Crea un nuevo transporte tras validar que existe ruta viable.

        Returns:
            (éxito, mensaje, transporte_o_None)
        """
        # Calcular ruta vía GPS
        ruta = GPS.calcular_ruta(mapa, origen, destino)
        if ruta is None:
            return False, f"❌ No existe ruta viable entre {origen} y {destino}.", None

        try:
            transporte = Transporte(
                origen=origen,
                destino=destino,
                ruta=ruta,
                tipo=tipo,
                tipo_recurso=tipo_recurso,
                cantidad=cantidad,
                velocidad=velocidad,
                propietario_id=propietario_id,
                metadata=metadata or {},
            )
        except ValueError as e:
            return False, f"❌ Error al crear transporte: {e}", None

        # Registrar en índices
        self._por_id[transporte.id] = transporte
        self._registrar_posicion(transporte.id, transporte.posicion_actual)

        return True, f"🚚 Transporte {transporte.id} creado ({len(ruta)} waypoints).", transporte

    # ==========================================
    # TICK LOGÍSTICO
    # ==========================================
    def avanzar_todos(self, mapa: Mapa) -> list[EventoLlegada]:
        """
        Avanza todos los transportes activos un tick.

        Returns:
            Lista de EventosLlegada para los transportes que alcanzaron destino.
            El llamador (ControladorPartida) debe procesar las transferencias
            y llamar a eliminar() para cada evento.
        """
        eventos: list[EventoLlegada] = []

        # Copia de IDs para evitar modificación durante iteración
        ids_activos = list(self._por_id.keys())

        for tid in ids_activos:
            transporte = self._por_id.get(tid)
            if transporte is None:
                continue  # Fue eliminado este mismo tick por otro evento

            # Desregistrar posición antigua
            self._desregistrar_posicion(tid, transporte.posicion_actual)

            # Avanzar
            ha_llegado, msg = transporte.avanzar(mapa)

            # Registrar nueva posición
            self._registrar_posicion(tid, transporte.posicion_actual)

            if ha_llegado:
                eventos.append(EventoLlegada(transporte=transporte, mensaje=msg))

        return eventos

    # ==========================================
    # ELIMINACIÓN
    # ==========================================
    def eliminar(self, transporte_id: str) -> bool:
        """Elimina un transporte del registro. Devuelve False si no existía."""
        transporte = self._por_id.pop(transporte_id, None)
        if transporte is None:
            return False
        self._desregistrar_posicion(transporte_id, transporte.posicion_actual)
        return True

    def cancelar(self, transporte_id: str) -> tuple[bool, str]:
        """Cancela un transporte activo (no transfiere carga)."""
        if self.eliminar(transporte_id):
            return True, f"🚫 Transporte {transporte_id} cancelado."
        return False, f"❌ Transporte {transporte_id} no encontrado."

    # ==========================================
    # CONSULTAS
    # ==========================================
    def obtener(self, transporte_id: str) -> Transporte | None:
        return self._por_id.get(transporte_id)

    def get_en_posicion(self, coord: Coordenada) -> list[Transporte]:
        """Devuelve todos los transportes actualmente en una coordenada."""
        ids = self._por_posicion.get(coord, [])
        return [self._por_id[tid] for tid in ids if tid in self._por_id]

    def get_por_propietario(self, propietario_id: str) -> list[Transporte]:
        """Devuelve todos los transportes de un Reino/Tribu."""
        return [t for t in self._por_id.values() if t.propietario_id == propietario_id]

    def get_por_tipo(self, tipo: TipoTransporte) -> list[Transporte]:
        """Filtra transportes por tipo."""
        return [t for t in self._por_id.values() if t.tipo == tipo]

    @property
    def total_activos(self) -> int:
        return len(self._por_id)

    def resumen(self) -> dict:
        """Resumen estadístico para debug / admin."""
        por_tipo: dict[str, int] = {}
        for t in self._por_id.values():
            por_tipo[t.tipo.value] = por_tipo.get(t.tipo.value, 0) + 1
        return {
            "total_activos": self.total_activos,
            "por_tipo": por_tipo,
        }

    # ==========================================
    # GESTIÓN INTERNA DE ÍNDICE POSICIONAL
    # ==========================================
    def _registrar_posicion(self, transporte_id: str, coord: Coordenada) -> None:
        if coord not in self._por_posicion:
            self._por_posicion[coord] = []
        if transporte_id not in self._por_posicion[coord]:
            self._por_posicion[coord].append(transporte_id)

    def _desregistrar_posicion(self, transporte_id: str, coord: Coordenada) -> None:
        lista = self._por_posicion.get(coord)
        if lista and transporte_id in lista:
            lista.remove(transporte_id)
            if not lista:
                del self._por_posicion[coord]

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        return f"🚚 GestorTransportes: {self.total_activos} activos"
