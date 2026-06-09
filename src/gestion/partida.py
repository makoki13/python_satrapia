# src/gestion/partida.py
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, ClassVar

from src.territorio.mapa import Mapa

if TYPE_CHECKING:
    from src.logistica.gestor_transportes import GestorTransportes
    from src.territorio.ciudad import Ciudad
    from src.territorio.reino import Reino


# ==========================================
# ENUMS Y CONFIGURACIÓN (Deben ir ANTES de Partida)
# ==========================================
class EstadoPartida(Enum):
    """Estados posibles del ciclo de vida de una partida."""
    LOBBY = auto()      # Esperando jugadores
    EN_CURSO = auto()   # Juego activo
    FINALIZADA = auto() # Terminó normalmente (victoria/derrota)
    CANCELADA = auto()  # Abortada antes de empezar o durante el juego


@dataclass
class ConfiguracionMapa:
    """
    Define los límites geográficos específicos para esta partida.
    Permite usar el tamaño de producción o un tamaño reducido para pruebas.
    """
    MAX_X: ClassVar[int] = 1000  # Tamaño producción
    MAX_Y: ClassVar[int] = 1000
    DEBUG_X: ClassVar[int] = 200  # Tamaño desarrollo
    DEBUG_Y: ClassVar[int] = 200

    max_x: int = field(default=MAX_X)
    max_y: int = field(default=MAX_Y)

    @classmethod
    def modo_desarrollo(cls) -> ConfiguracionMapa:
        """Crea una configuración con tamaño reducido para pruebas rápidas."""
        return cls(max_x=cls.DEBUG_X, max_y=cls.DEBUG_Y)

    @classmethod
    def modo_produccion(cls) -> ConfiguracionMapa:
        """Crea una configuración con tamaño completo del juego."""
        return cls(max_x=cls.MAX_X, max_y=cls.MAX_Y)


# ==========================================
# CLASE PARTIDA
# ==========================================
@dataclass
class Partida:
    """
    Representa una instancia de juego donde los usuarios se convierten en jugadores.
    Gestiona el estado, el mapa, y el ciclo de vida completo de la sesión.
    """

    # ==========================================
    # ATRIBUTOS OBLIGATORIOS
    # ==========================================
    nombre: str
    creador_id: str  # ID del Usuario que creó la partida

    # ==========================================
    # ATRIBUTOS CON VALOR POR DEFECTO
    # ==========================================
    estado: EstadoPartida = EstadoPartida.LOBBY
    turno_actual: int = 0
    configuracion_mapa: ConfiguracionMapa = field(default_factory=ConfiguracionMapa.modo_produccion)

    # ==========================================
    # ATRIBUTOS INTERNOS (init=False)
    # ==========================================
    id: str = field(init=False)
    fecha_creacion: datetime = field(init=False)
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None

    # Colecciones de sesión
    jugadores: list = field(default_factory=list)  # Lista de objetos Jugador
    mapa: Mapa = field(init=False)  # Siempre existirá, se crea en __post_init__

    # ==========================================
    # ENTIDADES DE JUEGO (Se inicializan al iniciar partida)
    # ==========================================
    reinos: list[Reino] = field(default_factory=list)
    ciudades: list[Ciudad] = field(default_factory=list)
    gestor_transportes: GestorTransportes | None = None

    # ==========================================
    # INICIALIZACIÓN
    # ==========================================
    def __post_init__(self):
        self.id = str(uuid.uuid4())
        self.fecha_creacion = datetime.now()
        self._inicializar_mapa()

    def _inicializar_mapa(self) -> None:
        """Crea el mapa con las dimensiones configuradas."""
        es_desarrollo = (self.configuracion_mapa.max_x < 500)
        self.mapa = Mapa(
            nombre=f"Mapa - {self.nombre}",
            modo_desarrollo=es_desarrollo
        )
        self.mapa.limite_x = self.configuracion_mapa.max_x
        self.mapa.limite_y = self.configuracion_mapa.max_y

    def _inicializar_entidades_juego(self) -> None:
        """
        Crea las entidades necesarias para el Server Tick.
        Debe llamarse desde iniciar_partida() tras validar jugadores.
        """
        from src.logistica.gestor_transportes import GestorTransportes

        if self.gestor_transportes is None:
            self.gestor_transportes = GestorTransportes()

        # Futuro: crear reinos a partir de jugadores, asignar capitales, etc.

    # ==========================================
    # GESTIÓN DE JUGADORES
    # ==========================================
    def añadir_jugador(self, jugador) -> bool:
        """Añade un jugador a la partida. Solo en LOBBY."""
        if self.estado != EstadoPartida.LOBBY:
            print(f"⚠️ No se pueden añadir jugadores. Estado actual: {self.estado.name}")
            return False

        if jugador in self.jugadores:
            print(f"⚠️ El jugador {jugador} ya está en la partida.")
            return False

        self.jugadores.append(jugador)
        print(f"✅ {jugador} se ha unido a '{self.nombre}'")
        return True

    def quitar_jugador(self, jugador) -> bool:
        """Elimina un jugador de la partida (si está en LOBBY)."""
        if self.estado != EstadoPartida.LOBBY:
            print(f"⚠️ No se pueden quitar jugadores. Estado actual: {self.estado.name}")
            return False

        if jugador in self.jugadores:
            self.jugadores.remove(jugador)
            print(f"✅ {jugador} ha salido de '{self.nombre}'")
            return True
        return False

    # ==========================================
    # CONTROL DE ESTADO
    # ==========================================
    def iniciar_partida(self) -> bool:
        """
        Transiciona la partida de LOBBY a EN_CURSO.
        Requiere al menos 2 jugadores. Inicializa entidades de juego.
        """
        if self.estado != EstadoPartida.LOBBY:
            print(f"⚠️ La partida no está en LOBBY. Estado: {self.estado.name}")
            return False

        if len(self.jugadores) < 2:
            print(f"⚠️ Se necesitan al menos 2 jugadores para empezar. Hay {len(self.jugadores)}.")
            return False

        self.estado = EstadoPartida.EN_CURSO
        self.fecha_inicio = datetime.now()
        self.turno_actual = 1

        # ✅ Inicializar entidades de juego
        self._inicializar_entidades_juego()

        print(f"🎮 ¡La partida '{self.nombre}' ha comenzado!")
        return True

    def finalizar_partida(self, motivo: str = "Victoria") -> None:
        """Marca la partida como finalizada."""
        if self.estado != EstadoPartida.EN_CURSO:
            print("⚠️ Solo se puede finalizar una partida en curso.")
            return

        self.estado = EstadoPartida.FINALIZADA
        self.fecha_cierre = datetime.now()
        print(f"🏁 Partida '{self.nombre}' finalizada. Motivo: {motivo}")

    def cancelar_partida(self, motivo: str = "Cancelada por el creador") -> None:
        """Cancela la partida (desde LOBBY o EN_CURSO)."""
        if self.estado == EstadoPartida.FINALIZADA:
            print("⚠️ No se puede cancelar una partida ya finalizada.")
            return

        self.estado = EstadoPartida.CANCELADA
        self.fecha_cierre = datetime.now()
        print(f"❌ Partida '{self.nombre}' cancelada. Motivo: {motivo}")

    # ==========================================
    # CONSULTAS PARA SERVER TICK
    # ==========================================
    def obtener_ciudad_en(self, coord) -> Ciudad | None:
        """Busca una ciudad por su ubicación en el mapa."""
        for ciudad in self.ciudades:
            if hasattr(ciudad, 'ubicacion') and ciudad.ubicacion == coord:
                return ciudad
        return None

    # ==========================================
    # INFORMACIÓN
    # ==========================================
    def get_duracion(self) -> str:
        """Calcula la duración de la partida si está finalizada."""
        if self.fecha_inicio and self.fecha_cierre:
            duracion = self.fecha_cierre - self.fecha_inicio
            horas, remainder = divmod(int(duracion.total_seconds()), 3600)
            minutos, segundos = divmod(remainder, 60)
            return f"{horas}h {minutos}m {segundos}s"
        return "En curso"

    def __str__(self) -> str:
        jugadores_str = f"{len(self.jugadores)} jugadores" if self.jugadores else "Sin jugadores"
        dimensiones = f"{self.configuracion_mapa.max_x}x{self.configuracion_mapa.max_y}"
        return (f"🎲 Partida: {self.nombre} | Estado: {self.estado.name} | "
                f"{jugadores_str} | Mapa: {dimensiones} km")


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Partida ---\n")

    # 1. Crear partida en modo producción
    print("=== Creando partida en MODO PRODUCCIÓN ===")
    partida_prod = Partida(
        nombre="La Gran Guerra Imperial",
        creador_id="user-123-abc"
    )
    print(f"✅ {partida_prod}")
    print(f"   ID: {partida_prod.id[:8]}...")
    print(f"   Creada: {partida_prod.fecha_creacion}")
    print(f"   Dimensiones del mapa: {partida_prod.mapa.get_dimensiones()}")

    # 2. Crear partida en modo desarrollo
    print("\n=== Creando partida en MODO DESARROLLO ===")
    config_dev = ConfiguracionMapa.modo_desarrollo()
    partida_dev = Partida(
        nombre="Test Rápido",
        creador_id="user-456-def",
        configuracion_mapa=config_dev
    )
    print(f"✅ {partida_dev}")
    print(f"   Dimensiones del mapa: {partida_dev.mapa.get_dimensiones()}")

    # 3. Ciclo de vida completo
    print("\n=== Probando ciclo de vida ===")

    jugador1 = "Jugador_A"
    jugador2 = "Jugador_B"
    jugador3 = "Jugador_C"

    print("\nIntentando iniciar sin jugadores suficientes:")
    partida_dev.añadir_jugador(jugador1)
    partida_dev.iniciar_partida()  # Debería fallar

    print("\nAñadiendo jugadores:")
    partida_dev.añadir_jugador(jugador2)
    partida_dev.añadir_jugador(jugador3)

    print("\nIniciando partida:")
    partida_dev.iniciar_partida()
    partida_dev.añadir_jugador("Jugador_Tardío")  # Debería fallar

    # Verificar que las entidades de juego se inicializaron
    print(f"\n✅ Gestor de transportes creado: {partida_dev.gestor_transportes is not None}")
    print(f"✅ Reinos inicializados: {len(partida_dev.reinos)}")
    print(f"✅ Ciudades inicializadas: {len(partida_dev.ciudades)}")

    print("\nSimulando avance de turnos:")
    for i in range(2, 6):
        partida_dev.turno_actual = i
        print(f"   Turno {partida_dev.turno_actual}")

    print("\nFinalizando partida:")
    partida_dev.finalizar_partida("Victoria del Emperador")
    print(f"   Duración: {partida_dev.get_duracion()}")
    print(f"   Estado final: {partida_dev}")

    # 4. Cancelar partida
    print("\n=== Probando cancelación ===")
    partida_cancel = Partida("Partida Fallida", "user-789")
    partida_cancel.cancelar_partida("El creador se desconectó")
    print(f"   {partida_cancel}")

    print("\n--- ✅ Fin de las pruebas ---")
