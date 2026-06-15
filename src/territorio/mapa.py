# src/territorio/mapa.py
"""
Módulo que define la clase Mapa, contenedor principal del mundo del juego.

El mapa es una cuadrícula de puntos (Coordenada → Punto) con dimensiones
configurables según el modo de operación (desarrollo o producción).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from src.core.coordenada import Coordenada

if TYPE_CHECKING:
    from src.territorio.punto import Punto


@dataclass
class Mapa:
    """
    Gestiona el mapa físico y político del juego.

    Atributos clave:
        - puntos: Diccionario {Coordenada → Punto} con todas las casillas registradas.
        - limite_x/limite_y: Dimensiones activas según el modo.
        - modo_desarrollo: Si True, usa límites reducidos (DEBUG_X × DEBUG_Y)
                          para pruebas rápidas.

    Los límites son EXCLUSIVOS: un mapa 200×200 tiene coordenadas válidas 0..199.
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
    puntos: dict[Coordenada, Punto] = field(default_factory=dict, init=False)

    # ==========================================
    # INICIALIZACIÓN
    # ==========================================
    def __post_init__(self):
        """Se ejecuta automáticamente después del __init__."""
        if not self.nombre.strip():
            raise ValueError("El nombre del mapa no puede estar vacío.")

        if self.modo_desarrollo:
            self.limite_x = self.DEBUG_X
            self.limite_y = self.DEBUG_Y
        else:
            self.limite_x = self.MAX_X
            self.limite_y = self.MAX_Y

    # ==========================================
    # VALIDACIONES
    # ==========================================
    def es_coordenada_valida(self, coordenada: Coordenada) -> bool:
        """
        Verifica si una coordenada está dentro de los límites activos del mapa.
        Los límites son EXCLUSIVOS: un mapa 200x200 tiene coords válidas 0..199.
        """
        return (
            0 <= coordenada.x < self.limite_x
            and 0 <= coordenada.y < self.limite_y
        )

    # ==========================================
    # PROPIEDADES
    # ==========================================
    @property
    def dimensiones(self) -> tuple[int, int]:
        """Devuelve (ancho, alto) del mapa en km."""
        return (self.limite_x, self.limite_y)

    @property
    def dimensiones_str(self) -> str:
        """Devuelve dimensiones formateadas como string legible."""
        return f"{self.limite_x}x{self.limite_y} km"

    @property
    def total_puntos(self) -> int:
        """Número de puntos registrados actualmente en el mapa."""
        return len(self.puntos)

    # ==========================================
    # GESTIÓN DE PUNTOS
    # ==========================================
    def registrar_punto(self, punto: Punto, sobrescribir: bool = False) -> bool:
        """
        Registra un punto en el mapa de forma segura.

        Args:
            punto: Punto a registrar.
            sobrescribir: Si True, reemplaza un punto existente en la misma coordenada.

        Returns:
            True si se registró correctamente, False si:
              - La coordenada está fuera de los límites del mapa.
              - Ya existe un punto en esa coordenada y no se permite sobrescribir.
        """
        if not self.es_coordenada_valida(punto.coordenada):
            return False
        if punto.coordenada in self.puntos and not sobrescribir:
            return False
        self.puntos[punto.coordenada] = punto
        return True

    # get es una función del diccionario. tiene un segundo parámetro
    # que es el valor devuelto si no se encuentra el elemento. Por defecto es 'None'
    def obtener_punto(self, coordenada: Coordenada) -> Punto | None:
        """Devuelve el punto en una coordenada, o None si no existe."""
        return self.puntos.get(coordenada)

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        modo = " [DESARROLLO]" if self.modo_desarrollo else " [PRODUCCIÓN]"
        return f"Mapa: {self.nombre}{modo} | Dimensiones: {self.dimensiones_str} | Puntos: {self.total_puntos}"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Mapa ---\n")

    mapa_real = Mapa("El Gran Continente", modo_desarrollo=False)
    print(f"✅ {mapa_real}")
    assert mapa_real.dimensiones == (1000, 1000)
    assert mapa_real.limite_x == 1000

    mapa_dev = Mapa("Mapa de Pruebas", modo_desarrollo=True)
    print(f"✅ {mapa_dev}")
    assert mapa_dev.dimensiones == (200, 200)

    print("\n--- Probando límites en Modo Desarrollo (200x200) ---")
    c_valida = Coordenada(150, 150)
    c_limite = Coordenada(199, 199)
    c_fuera = Coordenada(200, 200)
    c_invalida = Coordenada(500, 500)

    assert mapa_dev.es_coordenada_valida(c_valida), "150,150 debe ser válida"
    assert mapa_dev.es_coordenada_valida(c_limite), "199,199 debe ser válida"
    assert not mapa_dev.es_coordenada_valida(c_fuera), "200,200 debe ser inválida (límite exclusivo)"
    assert not mapa_dev.es_coordenada_valida(c_invalida), "500,500 debe ser inválida en DEV"
    assert mapa_real.es_coordenada_valida(c_invalida), "500,500 debe ser válida en REAL"

    print(f"   ✅ {c_valida} válida en DEV")
    print(f"   ✅ {c_limite} válida en DEV (borde del mapa)")
    print(f"   ✅ {c_fuera} inválida en DEV (justo fuera del borde)")
    print(f"   ✅ {c_invalida} inválida en DEV pero válida en REAL")

    print("\n--- Probando registro de puntos ---")
    from src.territorio.punto import Punto
    from src.territorio.terreno import TipoTerreno

    p1 = Punto(Coordenada(10, 10), terreno=TipoTerreno.LLANURA)
    p2 = Punto(Coordenada(20, 20), terreno=TipoTerreno.BOSQUE)

    assert mapa_dev.registrar_punto(p1) is True, "Primer registro debe funcionar"
    assert mapa_dev.registrar_punto(p1) is False, "Duplicado sin sobrescribir debe fallar"
    assert mapa_dev.registrar_punto(p1, sobrescribir=True) is True, "Sobrescribir debe funcionar"
    assert mapa_dev.total_puntos == 1

    mapa_dev.registrar_punto(p2)
    assert mapa_dev.total_puntos == 2
    assert mapa_dev.obtener_punto(Coordenada(10, 10)) == p1
    assert mapa_dev.obtener_punto(Coordenada(99, 99)) is None

    # Registro fuera de límites
    p_fuera = Punto(Coordenada(500, 500), terreno=TipoTerreno.LLANURA)
    assert mapa_dev.registrar_punto(p_fuera) is False, "Fuera de límites debe fallar"

    print(f"   ✅ Registro de puntos funcionando ({mapa_dev.total_puntos} puntos)")
    print(f"   ✅ Estado final: {mapa_dev}")

    print("\n✅ Todas las pruebas de Mapa pasaron correctamente.")
    print("\n--- Fin de las pruebas ---")
