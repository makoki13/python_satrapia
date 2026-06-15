# src/territorio/faccion.py
"""
Tipos de facciones políticas en el mundo de Satrapia.

Cada tipo de facción tiene características de juego distintas y suele
estar asociado a zonas geográficas específicas del mapa.
"""
from __future__ import annotations

from enum import Enum


class TipoFaccion(Enum):
    """
    Tipos de facciones que pueden ocupar territorio.

    - IMPERIO:  Zonas cardinales, fértiles, acceso a recursos abundantes.
                Reservado para el Emperador.
    - SATRAPIA: Zonas diagonales, equilibrio entre recursos y defensa.
                Reservado para los Sátrapas.
    - TRIBU:    Zonas fronterizas, estepas, movilidad alta pero recursos escasos.
                Reservado para los Jefes tribales.
    """
    IMPERIO = "Imperio"
    SATRAPIA = "Satrapía"
    TRIBU = "Tribu Nómada"

    def __str__(self) -> str:
        return self.value


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🏛️ Probando TipoFaccion ---\n")

    for faccion in TipoFaccion:
        print(f"   • {faccion.name:10} → {faccion.value}")

    assert str(TipoFaccion.IMPERIO) == "Imperio"
    assert TipoFaccion["SATRAPIA"] == TipoFaccion.SATRAPIA
    assert TipoFaccion("Tribu Nómada") == TipoFaccion.TRIBU

    print("\n✅ Todas las pruebas de TipoFaccion pasaron correctamente.")
