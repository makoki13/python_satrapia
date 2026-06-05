# src/territorio/tribu.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

from src.core.coordenada import Coordenada


@dataclass
class Tribu:
    """
    Representa una facción nómada que no tiene territorio fijo.
    Su campamento se mueve por el mapa y puede saquear o comerciar.
    """

    # ==========================================
    # CONSTANTES
    # ==========================================
    MAX_UNIDADES_NOMADAS: ClassVar[int] = 10

    # ==========================================
    # ATRIBUTOS OBLIGATORIOS
    # ==========================================
    nombre: str
    ubicacion_actual: Coordenada  # Coordenada del campamento

    # ==========================================
    # ATRIBUTOS CON VALOR POR DEFECTO
    # ==========================================
    lider: Any = None  # Objeto Jugador
    radio_influencia: int = 50  # Área de saqueo/recolección

    # Puntos que la tribu "controla" temporalmente (no son propietarios fijos)
    puntos_visitados: set[Any] = field(default_factory=set)

    # ==========================================
    # MÉTODOS
    # ==========================================
    def mover_campamento(self, nueva_ubicacion: Coordenada) -> None:
        """Mueve el campamento nómada a una nueva coordenada."""
        self.ubicacion_actual = nueva_ubicacion
        print(f"🏕️ La tribu {self.nombre} ha movido su campamento a {nueva_ubicacion}")

    def __str__(self) -> str:
        return f"Tribu {self.nombre} en {self.ubicacion_actual}"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🏕️ Probando Tribu ---\n")

    tribu_test = Tribu(nombre="Hijos del Viento", ubicacion_actual=Coordenada(100, 100))
    print(f"✅ {tribu_test}")

    tribu_test.mover_campamento(Coordenada(120, 130))
    print(f"✅ Después de mover: {tribu_test}")

    print("\n--- Fin de las pruebas ---")
