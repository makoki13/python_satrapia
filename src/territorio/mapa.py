# src/territorio/mapa.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

from src.core.coordenada import Coordenada


@dataclass
class Mapa:
    """
    Clase que gestiona el mapa físico y político del juego.
    """

    # ==========================================
    # CONSTANTES DE CLASE (No van al __init__)
    # ==========================================
    MAX_X: ClassVar[int] = 1000
    MAX_Y: ClassVar[int] = 1000
    DEBUG_X: ClassVar[int] = 200
    DEBUG_Y: ClassVar[int] = 200

    # ==========================================
    # PARÁMETROS DEL CONSTRUCTOR (__init__)
    # ==========================================
    nombre: str = "Mundo de Satrapia"
    modo_desarrollo: bool = False

    # ==========================================
    # ATRIBUTOS INTERNOS (Se calculan en __post_init__)
    # ==========================================
    limite_x: int = field(init=False)
    limite_y: int = field(init=False)
    puntos: dict[Coordenada, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        """Se ejecuta automáticamente después del __init__."""
        if self.modo_desarrollo:
            self.limite_x = self.DEBUG_X
            self.limite_y = self.DEBUG_Y
        else:
            self.limite_x = self.MAX_X
            self.limite_y = self.MAX_Y

    def es_coordenada_valida(self, coordenada: Coordenada) -> bool:
        """Verifica si una coordenada está dentro de los límites activos del mapa."""
        return (0 <= coordenada.x <= self.limite_x) and (0 <= coordenada.y <= self.limite_y)

    def get_dimensiones(self) -> str:
        return f"{self.limite_x}x{self.limite_y} km"

    def __str__(self) -> str:
        modo = " [DESARROLLO]" if self.modo_desarrollo else " [PRODUCCIÓN]"
        return f"Mapa: {self.nombre}{modo} | Dimensiones: {self.get_dimensiones()}"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Mapa ---\n")

    # Ahora el constructor solo pide 'nombre' y 'modo_desarrollo'
    mapa_real = Mapa("El Gran Continente", modo_desarrollo=False)
    print(f"✅ {mapa_real}")

    mapa_dev = Mapa("Mapa de Pruebas", modo_desarrollo=True)
    print(f"✅ {mapa_dev}")

    print("\n--- Probando límites en Modo Desarrollo (200x200) ---")
    c_valida = Coordenada(150, 150)
    c_invalida = Coordenada(500, 500)

    print(f"¿{c_valida} es válida en DEV? -> {mapa_dev.es_coordenada_valida(c_valida)} (Esperado: True)")
    print(f"¿{c_invalida} es válida en DEV? -> {mapa_dev.es_coordenada_valida(c_invalida)} (Esperado: False)")
    print(f"¿{c_invalida} es válida en REAL? -> {mapa_real.es_coordenada_valida(c_invalida)} (Esperado: True)")

    print("\n--- Fin de las pruebas ---")
