# src/territorio/zona_disponible.py
from dataclasses import dataclass
from enum import Enum

from src.core.coordenada import Coordenada


class TipoFaccion(Enum):
    """Tipos de facciones que pueden ocupar una zona."""
    IMPERIO = "Imperio"      # Para el Emperador (zonas cardinales, fértiles)
    SATRAPIA = "Satrapía"    # Para los Sátrapas (zonas diagonales)
    TRIBU = "Tribu Nómada"   # Para los Jefes (zonas fronterizas, estepas)


@dataclass
class ZonaDisponible:
    """
    Representa una región del mapa pre-reservada para que un jugador
    establezca su facción (Reino o Tribu) al unirse a la partida.
    """
    coordenada_central: Coordenada
    radio: int  # Radio en km (puntos) de la zona de influencia inicial
    tipo_faccion: TipoFaccion
    ocupada: bool = False

    def __str__(self) -> str:
        estado = "🔴 Ocupada" if self.ocupada else "🟢 Disponible"
        return f"Zona {self.tipo_faccion.value} en {self.coordenada_central} [{estado}]"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🗺️ Probando Zonas Disponibles ---\n")

    z1 = ZonaDisponible(Coordenada(500, 800), radio=50, tipo_faccion=TipoFaccion.IMPERIO)
    z2 = ZonaDisponible(Coordenada(200, 200), radio=30, tipo_faccion=TipoFaccion.TRIBU)

    print(f"✅ {z1}")
    print(f"✅ {z2}")
