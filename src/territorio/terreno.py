# src/territorio/terreno.py
from enum import Enum


class TipoTerreno(Enum):
    """
    Tipos de terreno disponibles en el mundo de Satrapia.
    Cada terreno define sus propiedades de juego (coste, transitabilidad, etc.).
    """

    # (nombre_legible, coste_movimiento, transitable, es_tierra, construible)
    LLANURA = ("Llanura", 1, True, True, True)
    BOSQUE = ("Bosque", 2, True, True, True)
    MONTAÑA = ("Montaña", 3, True, True, False)  # No construible salvo excepciones
    DESIERTO = ("Desierto", 2, True, True, False)
    ESTEPA = ("Estepa", 1, True, True, True)     # Ideal para nómadas
    MAR = ("Mar", 99, False, False, False)       # Intransitable sin barcos
    PASO_MONTAÑA = ("Paso de Montaña", 2, True, True, True)  # Estratégico
    COLINA = ("Colina", 2, True, True, True)

    def __init__(self, nombre: str, coste: int, transitable: bool, es_tierra: bool, construible: bool):
        self.nombre_legible = nombre
        self.coste_movimiento = coste
        self.transitable = transitable
        self.es_tierra = es_tierra
        self.construible = construible

    def __str__(self) -> str:
        return self.nombre_legible

    def es_agua(self) -> bool:
        """Alias para comprobar si es una casilla de agua."""
        return not self.es_tierra


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🗺️ Probando Tipos de Terreno ---\n")

    for terreno in TipoTerreno:
        print(f"• {terreno.nombre_legible:20} | Coste: {terreno.coste_movimiento} | "
              f"Transitable: {terreno.transitable} | Construible: {terreno.construible}")

    print(f"\n¿Se puede construir en el MAR? -> {TipoTerreno.MAR.construible}")
    print(f"¿La Llanura es tierra? -> {TipoTerreno.LLANURA.es_tierra}")
