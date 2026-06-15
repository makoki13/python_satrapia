# src/territorio/zona_disponible.py
"""
Zonas disponibles para que los jugadores establezcan sus facciones al unirse.

Cada zona tiene una coordenada central, un radio de influencia y un tipo de facción
asociado. Las zonas se marcan como ocupadas cuando un jugador funda su capital allí.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.core.coordenada import Coordenada
from src.territorio.faccion import TipoFaccion


@dataclass
class ZonaDisponible:
    """
    Representa una región del mapa pre-reservada para que un jugador
    establezca su facción (Reino o Tribu) al unirse a la partida.

    Attributes:
        coordenada_central: Punto central de la zona.
        radio: Radio en km (puntos) de la zona de influencia inicial.
        tipo_faccion: Tipo de facción que puede ocupar esta zona.
        ocupada: Si True, la zona ya tiene un jugador establecido.
    """

    # ==========================================
    # ATRIBUTOS OBLIGATORIOS
    # ==========================================
    coordenada_central: Coordenada
    radio: int
    tipo_faccion: TipoFaccion

    # ==========================================
    # ATRIBUTOS CON VALOR POR DEFECTO
    # ==========================================
    ocupada: bool = False

    # ==========================================
    # VALIDACIONES
    # ==========================================
    def __post_init__(self):
        """Valida los parámetros de la zona tras la inicialización."""
        if self.radio <= 0:
            raise ValueError(f"El radio debe ser positivo, recibido: {self.radio}")

    # ==========================================
    # PROPIEDADES
    # ==========================================
    @property
    def bounding_box(self) -> tuple[Coordenada, Coordenada]:
        """
        Devuelve las coordenadas mínima y máxima de la zona (bounding box).

        Returns:
            Tupla (coord_min, coord_max) donde:
              - coord_min = (centro.x - radio, centro.y - radio)
              - coord_max = (centro.x + radio, centro.y + radio)
        """
        min_coord = Coordenada(
            self.coordenada_central.x - self.radio,
            self.coordenada_central.y - self.radio,
        )
        max_coord = Coordenada(
            self.coordenada_central.x + self.radio,
            self.coordenada_central.y + self.radio,
        )
        return (min_coord, max_coord)

    # ==========================================
    # MÉTODOS DE CONSULTA
    # ==========================================
    def contiene(self, coordenada: Coordenada) -> bool:
        """
        Verifica si una coordenada está dentro de la zona de influencia.

        Usa distancia Manhattan (|dx| + |dy|) para definir la zona como un rombo
        en lugar de un círculo, lo cual es más apropiado para mapas en cuadrícula.

        Args:
            coordenada: Coordenada a verificar.

        Returns:
            True si la coordenada está dentro del radio de la zona.
        """
        return self.distancia_al_centro(coordenada) <= self.radio

    def distancia_al_centro(self, coordenada: Coordenada) -> int:
        """
        Calcula la distancia Manhattan desde una coordenada al centro de la zona.

        Args:
            coordenada: Coordenada de referencia.

        Returns:
            Distancia en km (puntos) usando métrica Manhattan.
        """
        dx = abs(coordenada.x - self.coordenada_central.x)
        dy = abs(coordenada.y - self.coordenada_central.y)
        return dx + dy

    # ==========================================
    # MÉTODOS DE ESTADO
    # ==========================================
    def ocupar(self) -> bool:
        """
        Marca la zona como ocupada.

        Returns:
            True si se ocupó correctamente, False si ya estaba ocupada.
        """
        if self.ocupada:
            return False
        self.ocupada = True
        return True

    def liberar(self) -> bool:
        """
        Marca la zona como disponible (libre).

        Returns:
            True si se liberó correctamente, False si ya estaba libre.
        """
        if not self.ocupada:
            return False
        self.ocupada = False
        return True

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        estado = "Ocupada" if self.ocupada else "Disponible"
        icono = "🔴" if self.ocupada else "🟢"
        return (
            f"Zona {self.tipo_faccion.value} en {self.coordenada_central} "
            f"(radio={self.radio}) [{icono} {estado}]"
        )


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🗺️ Probando Zonas Disponibles ---\n")

    # 1. Crear zonas de prueba
    z1 = ZonaDisponible(Coordenada(500, 800), radio=50, tipo_faccion=TipoFaccion.IMPERIO)
    z2 = ZonaDisponible(Coordenada(200, 200), radio=30, tipo_faccion=TipoFaccion.TRIBU)

    print(f"✅ {z1}")
    print(f"✅ {z2}")

    assert z1.ocupada is False, "Zona nueva debe estar disponible"
    assert z2.ocupada is False, "Zona nueva debe estar disponible"

    # 2. Probar método contiene
    print("\n--- Probando método contiene() ---")
    coord_dentro = Coordenada(510, 810)  # Distancia Manhattan = 10 + 10 = 20 <= 50
    coord_fuera = Coordenada(600, 900)   # Distancia Manhattan = 100 + 100 = 200 > 50
    coord_borde = Coordenada(550, 800)   # Distancia Manhattan = 50 + 0 = 50 <= 50

    assert z1.contiene(coord_dentro), f"{coord_dentro} debe estar dentro de z1"
    assert not z1.contiene(coord_fuera), f"{coord_fuera} debe estar fuera de z1"
    assert z1.contiene(coord_borde), f"{coord_borde} debe estar en el borde de z1"

    print(f"   ✅ {coord_dentro} dentro de z1 (dist={z1.distancia_al_centro(coord_dentro)})")
    print(f"   ✅ {coord_fuera} fuera de z1 (dist={z1.distancia_al_centro(coord_fuera)})")
    print(f"   ✅ {coord_borde} en borde de z1 (dist={z1.distancia_al_centro(coord_borde)})")

    # 3. Probar bounding box
    print("\n--- Probando bounding_box ---")
    min_coord, max_coord = z1.bounding_box
    assert min_coord == Coordenada(450, 750), f"Min debe ser (450, 750), recibido {min_coord}"
    assert max_coord == Coordenada(550, 850), f"Max debe ser (550, 850), recibido {max_coord}"

    print(f"   ✅ Bounding box de z1: {min_coord} → {max_coord}")

    # 4. Probar ocupar/liberar
    print("\n--- Probando ocupar() y liberar() ---")
    assert z1.ocupar() is True, "Primera ocupación debe funcionar"
    assert z1.ocupada is True, "Zona debe estar marcada como ocupada"
    assert z1.ocupar() is False, "Segunda ocupación debe fallar (ya está ocupada)"

    print(f"   ✅ {z1}")

    assert z1.liberar() is True, "Liberación debe funcionar"
    assert z1.ocupada is False, "Zona debe estar marcada como disponible"
    assert z1.liberar() is False, "Segunda liberación debe fallar (ya está libre)"

    print(f"   ✅ {z1}")

    # 5. Probar validación de radio
    print("\n--- Probando validación de radio ---")
    try:
        ZonaDisponible(Coordenada(0, 0), radio=-10, tipo_faccion=TipoFaccion.IMPERIO)
        raise AssertionError("Debería haber lanzado ValueError")
    except ValueError as e:
        print(f"   ✅ Validación correcta: {e}")

    print("\n✅ Todas las pruebas de ZonaDisponible pasaron correctamente.")
    print("\n--- Fin de las pruebas ---")
