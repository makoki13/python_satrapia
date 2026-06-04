# src/territorio/punto.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from src.core.coordenada import Coordenada


class TipoTerreno(Enum):
    """Definición de los terrenos físicos del mapa."""
    LLANURA = auto()
    BOSQUE = auto()
    MONTAÑA = auto()
    MAR = auto()
    DESIERTO = auto()
    PICO = auto()  # Intransitable (cumbres nevadas o escarpadas)

@dataclass
class Punto:
    """
    Representa una casilla o nodo del mapa con sus características físicas y políticas.
    Es mutable, ya que su propietario o estado pueden cambiar durante la partida.
    """

    coordenada: Coordenada
    tipo_terreno: TipoTerreno
    propietario: Any = None  # Futuro: Aquí vincularemos al objeto 'Reino'

    def get_costo_movimiento(self, tipo_unidad: str = "terrestre") -> int:
        """
        Devuelve el costo de movimiento (en puntos de acción/turno) para entrar en este punto.
        Un valor de 999 se considera intransitable.
        """
        # Tabla de costos de movimiento base
        costos_base = {
            TipoTerreno.LLANURA: 1,
            TipoTerreno.BOSQUE: 2,
            TipoTerreno.DESIERTO: 2,
            TipoTerreno.MONTAÑA: 3,
            TipoTerreno.MAR: 999,
            TipoTerreno.PICO: 999  # Los picos son muros naturales
        }

        costo = costos_base.get(self.tipo_terreno, 1)

        # Lógica especial: El mar es infranqueable para unidades terrestres
        if self.tipo_terreno == TipoTerreno.MAR and tipo_unidad == "terrestre":
            return 999

        return costo

    def es_intransitable(self, tipo_unidad: str = "terrestre") -> bool:
        """Método auxiliar rápido para saber si una unidad puede pisar esta casilla."""
        return self.get_costo_movimiento(tipo_unidad) >= 999

    def __str__(self) -> str:
        dueno = getattr(self.propietario, 'nombre', "Tierra de nadie")
        return f"Punto en {self.coordenada} | Terreno: {self.tipo_terreno.name} | Dueño: {dueno}"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Punto ---\n")

    # Creamos distintos tipos de terreno en diferentes coordenadas
    p_llanura = Punto(Coordenada(1, 1), TipoTerreno.LLANURA)
    p_montana = Punto(Coordenada(1, 2), TipoTerreno.MONTAÑA)
    p_mar = Punto(Coordenada(1, 3), TipoTerreno.MAR)
    p_pico = Punto(Coordenada(1, 4), TipoTerreno.PICO)

    print(f"✅ {p_llanura}")
    print(f"✅ {p_montana}")
    print(f"✅ {p_mar}")
    print(f"✅ {p_pico}\n")

    # Probamos los costos de movimiento para una unidad terrestre
    print("--- Costos de movimiento (Unidad Terrestre) ---")
    print(f"Llanura: {p_llanura.get_costo_movimiento('terrestre')} (Esperado: 1)")
    print(f"Montaña: {p_montana.get_costo_movimiento('terrestre')} (Esperado: 3)")
    print(f"Mar: {p_mar.get_costo_movimiento('terrestre')} (Esperado: 999 - Intransitable)")
    print(f"Pico: {p_pico.get_costo_movimiento('terrestre')} (Esperado: 999 - Intransitable)\n")

    # Probamos el método auxiliar
    print(f"¿El Pico es intransitable? {p_pico.es_intransitable('terrestre')} (Esperado: True)")

    print("\n--- Fin de las pruebas ---")
