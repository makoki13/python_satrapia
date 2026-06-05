# src/territorio/punto.py
from dataclasses import dataclass, field
from typing import Any

from src.core.coordenada import Coordenada
from src.territorio.terreno import TipoTerreno


@dataclass
class Punto:
    """
    Representa una casilla del mapa (1 km²).
    Contiene información sobre el terreno, propietario y posibles estructuras.
    """

    # ==========================================
    # ATRIBUTOS OBLIGATORIOS
    # ==========================================
    coordenada: Coordenada

    # ==========================================
    # ATRIBUTOS CON VALOR POR DEFECTO
    # ==========================================
    # Por defecto, toda casilla nueva es una llanura (terreno neutro)
    terreno: TipoTerreno = TipoTerreno.LLANURA
    elevacion: int = 0  # Para el futuro: altura sobre el nivel del mar

    # Propietario (Reino, Tribu o None). Usamos Any por flexibilidad.
    propietario: Any = None

    # Aquí guardaremos referencias a ciudades, ejércitos, etc. (futuro)
    estructura: Any = None
    unidades: list = field(default_factory=list)

    # ==========================================
    # PROPIEDADES DERIVADAS (Del terreno)
    # ==========================================
    def es_transitable(self) -> bool:
        """Indica si una unidad terrestre puede pasar por aquí."""
        return self.terreno.transitable

    def es_tierra(self) -> bool:
        """Indica si es una casilla de tierra (no agua)."""
        return self.terreno.es_tierra

    def es_agua(self) -> bool:
        """Indica si es una casilla de agua."""
        return self.terreno.es_agua()

    def es_construible(self) -> bool:
        """Indica si se puede construir una ciudad o edificio aquí."""
        return self.terreno.construible and self.estructura is None

    def get_coste_movimiento(self) -> int:
        """Devuelve el coste de movimiento para atravesar este punto."""
        return self.terreno.coste_movimiento

    def __hash__(self) -> int:
        """
        Define la identidad del punto para poder usarlo en sets.
        Dos puntos son el mismo si tienen la misma coordenada,
        independientemente de su terreno o dueño actual.
        """
        return hash(self.coordenada)

    # ==========================================
    # MÉTODOS
    # ==========================================
    def tiene_propietario(self) -> bool:
        """Devuelve True si el punto pertenece a algún Reino o Tribu."""
        return self.propietario is not None

    def __str__(self) -> str:
        dueno = getattr(self.propietario, 'nombre', 'Tierra de nadie')
        return f"Punto{self.coordenada} [{self.terreno}] - {dueno}"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 📍 Probando Puntos del Mapa ---\n")

    # 1. Punto por defecto (llanura)
    p1 = Punto(Coordenada(50, 50))
    print(f"✅ {p1}")
    print(f"   Transitable: {p1.es_transitable()} | Construible: {p1.es_construible()}")

    # 2. Punto de montaña
    p2 = Punto(Coordenada(51, 50), terreno=TipoTerreno.MONTAÑA)
    print(f"\n✅ {p2}")
    print(f"   Transitable: {p2.es_transitable()} | Construible: {p2.es_construible()}")
    print(f"   Coste de movimiento: {p2.get_coste_movimiento()} (vs llanura: {p1.get_coste_movimiento()})")

    # 3. Punto de mar
    p3 = Punto(Coordenada(52, 50), terreno=TipoTerreno.MAR)
    print(f"\n✅ {p3}")
    print(f"   ¿Es agua? {p3.es_agua()} | ¿Transitable por tierra? {p3.es_transitable()}")

    print("\n--- Fin de las pruebas ---")
