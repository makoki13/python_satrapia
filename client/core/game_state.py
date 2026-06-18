# client/core/game_state.py
"""
Estado global reactivo del cliente Satrapia.

Patrón de diseño:
    - Singleton: solo existe una instancia accesible desde cualquier parte.
    - Señales Qt: la UI se suscribe a cambios y se actualiza automáticamente.
    - Estado canónico: una única fuente de verdad para partida, jugador y mapa.

Uso desde cualquier widget:
    from client.core.game_state import game_state

    # Suscribirse a cambios
    game_state.partida_actualizada.connect(mi_widget.refrescar)

    # Leer estado
    if game_state.partida:
        print(game_state.partida["nombre"])
"""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal


class GameState(QObject):
    """
    Estado global del cliente. Hereda de QObject para poder emitir señales.

    Señales principales:
        - conectado_al_servidor: El servidor respondió correctamente.
        - partida_actualizada: Los datos de la partida han cambiado.
        - jugador_asignado: El jugador local recibió su facción/capital.
        - turno_avanzado: El servidor avanzó un turno.
        - error_ocurrido: Algo falló (mensaje de error como argumento).
    """

    # ==========================================
    # SEÑALES (La UI se conecta a estas)
    # ==========================================
    conectado_al_servidor = Signal()
    desconectado_del_servidor = Signal()
    partida_actualizada = Signal(dict)       # Pasa los datos de la partida
    jugador_asignado = Signal(dict)          # Pasa los datos del jugador
    turno_avanzado = Signal(int)             # Pasa el número de turno
    error_ocurrido = Signal(str)             # Pasa el mensaje de error
    estado_conexion_cambiado = Signal(str)   # "conectando" | "conectado" | "desconectado"

    # ==========================================
    # CONSTRUCTOR
    # ==========================================
    def __init__(self):
        super().__init__()

        # ── Estado de conexión ──────────────────────────────────────────
        self.servidor_url: str = "http://localhost:8000"
        self.estado_conexion: str = "desconectado"  # "conectando" | "conectado" | "desconectado"

        # ── Estado de partida ───────────────────────────────────────────
        self.partida_id: str | None = None
        self.partida: dict[str, Any] | None = None   # Datos crudos de la API

        # ── Estado del jugador local ────────────────────────────────────
        self.jugador: dict[str, Any] | None = None   # Datos del jugador actual
        self.username: str | None = None
        self.rol: str | None = None
        self.faccion_nombre: str | None = None
        self.capital_nombre: str | None = None
        self.posicion_inicial: dict[str, int] | None = None

        # ── Estado del mundo ────────────────────────────────────────────
        self.mapa_dimensiones: tuple[int, int] | None = None
        self.turno_actual: int = 0
        self.ciudades: list[dict] = []
        self.edificios: list[dict] = []
        self.transportes: list[dict] = []

    # ==========================================
    # MÉTODOS DE ACTUALIZACIÓN (Los llama api_client)
    # ==========================================
    def set_conexion(self, estado: str) -> None:
        """Actualiza el estado de conexión y emite señal."""
        self.estado_conexion = estado
        self.estado_conexion_cambiado.emit(estado)

        if estado == "conectado":
            self.conectado_al_servidor.emit()
        elif estado == "desconectado":
            self.desconectado_del_servidor.emit()

    def set_partida(self, datos: dict[str, Any]) -> None:
        """Actualiza los datos de la partida activa."""
        self.partida = datos
        self.partida_id = datos.get("id")
        self.mapa_dimensiones = tuple(datos.get("dimensiones_mapa", "0x0").split("x"))
        self.partida_actualizada.emit(datos)

    def set_jugador(self, datos: dict[str, Any]) -> None:
        """Actualiza los datos del jugador local tras unirse a una partida."""
        self.jugador = datos
        self.username = datos.get("username")
        self.rol = datos.get("rol")
        self.faccion_nombre = datos.get("faccion_nombre")
        self.capital_nombre = datos.get("capital_nombre")
        self.posicion_inicial = datos.get("posicion_inicial")
        self.jugador_asignado.emit(datos)

    def set_turno(self, turno: int) -> None:
        """Actualiza el turno actual."""
        self.turno_actual = turno
        self.turno_avanzado.emit(turno)

    def reportar_error(self, mensaje: str) -> None:
        """Emite una señal de error para que la UI la muestre."""
        self.error_ocurrido.emit(mensaje)

    # ==========================================
    # MÉTODOS DE LIMPIEZA
    # ==========================================
    def reset(self) -> None:
        """Reinicia todo el estado (al desconectar o cambiar de partida)."""
        self.partida_id = None
        self.partida = None
        self.jugador = None
        self.username = None
        self.rol = None
        self.faccion_nombre = None
        self.capital_nombre = None
        self.posicion_inicial = None
        self.mapa_dimensiones = None
        self.turno_actual = 0
        self.ciudades.clear()
        self.edificios.clear()
        self.transportes.clear()

    # ==========================================
    # PROPIEDADES DE CONSULTA
    # ==========================================
    @property
    def esta_conectado(self) -> bool:
        return self.estado_conexion == "conectado"

    @property
    def tiene_partida(self) -> bool:
        return self.partida is not None

    @property
    def tiene_jugador(self) -> bool:
        return self.jugador is not None

    @property
    def esta_en_juego(self) -> bool:
        """True si hay partida activa Y jugador asignado."""
        return self.tiene_partida and self.tiene_jugador


# ==========================================
# INSTANCIA GLOBAL (Singleton)
# ==========================================
# Se crea una sola vez al importar el módulo.
# Desde cualquier parte del cliente:
#   from client.core.game_state import game_state
game_state = GameState()
