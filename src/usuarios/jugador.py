# src/usuarios/jugador.py
from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.gestion.partida import Partida
from src.usuarios.usuario import Usuario


class Rol(Enum):
    """Roles asimétricos disponibles en el mundo de Satrapia."""
    EMPERADOR = "Emperador"
    SATRAPA = "Sátrapa"
    JEFE = "Jefe Nómada"


class EstadoJugador(Enum):
    """Ciclo de vida de un jugador dentro de una partida."""
    EN_LOBBY = "En Lobby"
    ACTIVO = "Activo"
    ELIMINADO = "Eliminado"
    VENCEDOR = "Vencedor"
    DESCONECTADO = "Desconectado"


@dataclass
class Jugador:
    """
    Representa la encarnación de un Usuario dentro de una Partida específica.
    Gestiona su rol, su estado y su facción (Reino o Tribu).
    """

    # ==========================================
    # ATRIBUTOS OBLIGATORIOS
    # ==========================================
    usuario: Usuario
    partida: Partida
    nombre_partida: str  # El nombre de su personaje, reino o tribu en esta sesión

    # ==========================================
    # ATRIBUTOS CON VALOR POR DEFECTO
    # ==========================================
    rol: Rol | None = None
    estado: EstadoJugador = EstadoJugador.EN_LOBBY

    # ==========================================
    # REFERENCIAS AL MUNDO DEL JUEGO
    # ==========================================
    # Aquí guardaremos el objeto 'Reino' o 'Tribu'.
    faccion: Any = None

    # ==========================================
    # VALIDACIONES AL CREAR
    # ==========================================
    def __post_init__(self):
        if not self.nombre_partida.strip():
            raise ValueError("El nombre en la partida no puede estar vacío.")
        if len(self.nombre_partida) > 30:
            raise ValueError("El nombre en la partida es demasiado largo (máx 30 caracteres).")

    # ==========================================
    # MÉTODOS DE GESTIÓN
    # ==========================================
    def asignar_rol(self, rol: Rol) -> None:
        """Asigna el destino político del jugador en la partida."""
        self.rol = rol
        print(f"👑 {self.nombre_partida} ha recibido el rol de {self.rol.value}.")

    def asignar_faccion(self, faccion: Any) -> None:
        """Vincula al jugador con su Reino o Tribu correspondiente en el mapa."""
        self.faccion = faccion
        print(f"🏰 {self.nombre_partida} ahora controla: {getattr(faccion, 'nombre', 'Facción desconocida')}")

    def activar(self) -> None:
        """Marca al jugador como listo cuando la partida comienza."""
        if self.estado == EstadoJugador.EN_LOBBY:
            self.estado = EstadoJugador.ACTIVO

    def eliminar(self, motivo: str = "Derrotado") -> None:
        """Marca al jugador como eliminado (su reino cae o su tribu es dispersada)."""
        if self.estado == EstadoJugador.ACTIVO:
            self.estado = EstadoJugador.ELIMINADO
            print(f"💀 {self.nombre_partida} ha sido eliminado. Motivo: {motivo}")

    def declarar_vencedor(self) -> None:
        """Marca al jugador como ganador de la partida."""
        self.estado = EstadoJugador.VENCEDOR
        print(f"🏆 ¡{self.nombre_partida} ha logrado la victoria!")

    def __str__(self) -> str:
        rol_str = self.rol.value if self.rol else "Sin asignar"
        return f"Jugador: {self.nombre_partida} ({rol_str}) | Estado: {self.estado.value}"


# ==========================================
# BLOQUE DE PRUEBAS (Usando clases reales)
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Jugador ---\n")

    # 1. Creamos un Usuario real (esto ejecutará bcrypt, es normal que tarde medio segundo)
    print("=== Preparando entorno real ===")
    usuario_real_1 = Usuario(
        username="juan_perez",
        email="juan@satrapia.com",
        _password_hash="PasswordSegura123!"
    )
    print(f"✅ Usuario 1 creado: {usuario_real_1.username}")

    usuario_real_2 = Usuario(
        username="maria_nomada",
        email="maria@satrapia.com",
        _password_hash="OtraPassword456!"
    )
    print(f"✅ Usuario 2 creado: {usuario_real_2.username}")

    # 2. Creamos una Partida real (usando el ID del primer usuario como creador)
    partida_real = Partida(
        nombre="La Gran Guerra Imperial",
        creador_id=usuario_real_1.id
    )
    print(f"✅ Partida creada: {partida_real.nombre} (Mapa: {partida_real.mapa.get_dimensiones()})")

    # 3. Crear jugadores usando los objetos REALES
    print("\n=== Creando Jugadores ===")
    j1 = Jugador(usuario=usuario_real_1, partida=partida_real, nombre_partida="Ciro el Grande")
    j2 = Jugador(usuario=usuario_real_2, partida=partida_real, nombre_partida="Tribu del Viento")

    print(f"✅ {j1}")
    print(f"✅ {j2}")

    # 4. Asignar roles asimétricos
    print("\n=== Asignando Roles ===")
    j1.asignar_rol(Rol.EMPERADOR)
    j2.asignar_rol(Rol.JEFE)

    # 5. Simular unión a la partida y activación
    print("\n=== Añadiendo a la Partida y Activando ===")
    partida_real.añadir_jugador(j1)
    partida_real.añadir_jugador(j2)

    j1.activar()
    j2.activar()
    print(f"Estado de {j1.nombre_partida}: {j1.estado.value}")
    print(f"Estado de la partida: {partida_real.estado.name}")

    # 6. Simular eliminación
    print("\n=== Simulando Combate ===")
    j2.eliminar("Su campamento fue saqueado por las legiones imperiales")

    print("\n--- Fin de las pruebas ---")
