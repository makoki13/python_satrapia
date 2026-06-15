# src/core/coordenada.py
import math

# FrozenInstanceError deriva de AttributeError la cual deriva de Exception
# Exception de BaseException
from dataclasses import FrozenInstanceError, dataclass


@dataclass(frozen=True) # Inmutable: una vez creada, no puede cambiar.
class Coordenada:
    """Representa una posición única en el espacio del juego."""
    x: int
    y: int
    z: int = 0 # Útil para altitud o para sistemas de hexágonos cúbicos

    def distancia_a(self, otra: 'Coordenada') -> float:
        """Calcula la distancia euclidiana en línea recta a otra coordenada."""
        return math.sqrt(
            (self.x - otra.x)**2 +
            (self.y - otra.y)**2 +
            (self.z - otra.z)**2
        )

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Coordenada ---\n")

    # 1. Crear coordenadas (Probando el valor por defecto de z)
    c1 = Coordenada(0, 0)
    c2 = Coordenada(3, 4, 0)
    c3 = Coordenada(0, 0, 10) # Misma X e Y que c1, pero distinta altura
    c4 = Coordenada(0,0)

    print(f"Coordenada 1 creada: {c1}")
    print(f"Coordenada 2 creada: {c2}")
    print(f"Coordenada 3 creada: {c3}")

    # 2. Probar cálculo de distancia (Teorema de Pitágoras: 3, 4, 5)
    distancia_c1_c2 = c1.distancia_a(c2)
    print(f"\n📏 Distancia entre {c1} y {c2}: {distancia_c1_c2} (Debería ser 5.0)")

    distancia_c1_c3 = c1.distancia_a(c3)
    print(f"📏 Distancia entre {c1} y {c3}: {distancia_c1_c3} (Debería ser 10.0)")

    # 3. Probar la inmutabilidad (El superpoder de frozen=True)
    print("\n--- Probando inmutabilidad ---")
    print(f"Intentando cambiar la X de {c1} a 100...")

    try:
        c1.x = 100  # type: ignore # Esto debería fallar y saltar al except
        print("❌ ¡ERROR! Se pudo modificar la coordenada. El juego tendría bugs.")
    except FrozenInstanceError:
        print("✅ ¡ÉXITO! Python bloqueó la modificación. La coordenada es segura e inmutable.")

    print(c1.__eq__(c4))

    print("\n--- Fin de las pruebas ---")
