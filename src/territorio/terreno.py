# src/territorio/terreno.py
"""
Tipos de terreno disponibles en el mundo de Satrapia.

Cada terreno define sus propiedades de juego: coste de movimiento,
transitabilidad, si es tierra/agua, y si permite construcción.
"""

# Para poder utilizar tipos como list[TipoTerreno] en versiones antiguas de Python
from __future__ import annotations

from enum import Enum
from math import inf


class TipoTerreno(Enum):
    """
    Tipos de terreno del mapa.

    FORMATO DE TUPLA: (nombre_legible, coste_movimiento, transitable, es_tierra, construible)

    - coste_movimiento: entero > 0 para transitables; inf para intransitables
    - transitable: True si unidades terrestres pueden pasar
    - es_tierra: True si no es agua (inverso de es_agua)
    - construible: True si permite ciudades/edificios
    """

    # ==========================================
    # TERRENOS DE TIERRA TRANSITABLES Y CONSTRUIBLES
    # ==========================================
    LLANURA = ("Llanura", 1, True, True, True)
    BOSQUE = ("Bosque", 2, True, True, True)
    ESTEPA = ("Estepa", 1, True, True, True)       # Ideal para nómadas
    PASO_MONTAÑA = ("Paso de Montaña", 2, True, True, True)  # Estratégico
    COLINA = ("Colina", 2, True, True, True)

    # ==========================================
    # TERRENOS DE TIERRA TRANSITABLES PERO NO CONSTRUIBLES
    # ==========================================
    MONTAÑA = ("Montaña", 3, True, True, False)
    DESIERTO = ("Desierto", 2, True, True, False)

    # ==========================================
    # TERRENOS DE AGUA (INTRANSITABLES POR TIERRA)
    # ==========================================
    MAR = ("Mar", inf, False, False, False)

    # ==========================================
    # INICIALIZACIÓN
    # ==========================================
    def __init__(
        self,
        nombre: str,
        coste: float,
        transitable: bool,
        es_tierra: bool,
        construible: bool,
    ):
        self.nombre_legible = nombre
        self.coste_movimiento = coste
        self.transitable = transitable
        self.es_tierra = es_tierra
        self.construible = construible

    def __str__(self) -> str:
        return self.nombre_legible

    # ==========================================
    # PROPIEDADES DERIVADAS
    # ==========================================
    @property
    def es_agua(self) -> bool:
        """Indica si es una casilla de agua (no tierra)."""
        return not self.es_tierra

    # ==========================================
    # MÉTODOS DE UTILIDAD (Consultas globales)
    # ==========================================
    @classmethod
    def todos_transitables(cls) -> list[TipoTerreno]:
        """Devuelve todos los terrenos por los que puede pasar una unidad terrestre."""
        return [t for t in cls if t.transitable]

    @classmethod
    def todos_construibles(cls) -> list[TipoTerreno]:
        """Devuelve todos los terrenos que permiten construir ciudades/edificios."""
        return [t for t in cls if t.construible]

    @classmethod
    def todos_tierra(cls) -> list[TipoTerreno]:
        """Devuelve todos los terrenos que no son agua."""
        return [t for t in cls if t.es_tierra]


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🗺️ Probando Tipos de Terreno ---\n")

    for terreno in TipoTerreno:
        coste_str = "∞" if terreno.coste_movimiento == inf else str(terreno.coste_movimiento)
        print(
            f"• {terreno.nombre_legible:20} | "
            f"Coste: {coste_str:>3} | "
            f"Transitable: {str(terreno.transitable):5} | "
            f"Construible: {terreno.construible}"
        )

    print("\n🔍 Consultas específicas:")
    print(f"   ¿Se puede construir en el MAR? -> {TipoTerreno.MAR.construible}")
    print(f"   ¿La Llanura es tierra? -> {TipoTerreno.LLANURA.es_tierra}")
    print(f"   ¿El Mar es agua? -> {TipoTerreno.MAR.es_agua}")  # ← Ahora sin ()

    print(f"\n📋 Terrenos transitables: {[t.nombre_legible for t in TipoTerreno.todos_transitables()]}")
    print(f"📋 Terrenos construibles: {[t.nombre_legible for t in TipoTerreno.todos_construibles()]}")
    print(f"📋 Terrenos de tierra: {[t.nombre_legible for t in TipoTerreno.todos_tierra()]}")
