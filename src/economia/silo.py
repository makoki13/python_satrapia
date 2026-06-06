# src/economia/silo.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config.game_config import GameConfig


class TipoRecurso(Enum):
    """Recursos que puede almacenar un silo."""
    COMIDA = "Comida"
    MADERA = "Madera"
    PIEDRA = "Piedra"
    HIERRO = "Hierro"
    ORO = "Oro"
    POBLACION = "Población"
    # Recursos militares (unidades como recurso)
    INFANTERIA = "Infantería"
    CABALLERIA = "Caballería"
    ARQUEROS = "Arqueros"
    LANCEROS = "Lanceros"
    MAQUINAS_ASALTO = "Máquinas de Asalto"
    OFICIALES = "Oficiales"


@dataclass
class Silo:
    """
    Unidad atómica de almacenamiento.
    Siempre pertenece a un Almacén (relación N:1 gestionada desde el Almacén).

    Un silo almacena UN solo tipo de recurso con capacidad limitada.
    La capacidad efectiva = capacidad_base + bonus_investigacion.
    """

    # ==========================================
    # IDENTIDAD Y CONFIGURACIÓN
    # ==========================================
    nombre: str
    tipo_recurso: TipoRecurso
    capacidad_base: int           # Capacidad intrínseca (no cambia)

    # ==========================================
    # ESTADO DINÁMICO
    # ==========================================
    stock_actual: int = 0

    # ==========================================
    # VALIDACIONES
    # ==========================================
    def __post_init__(self):
        if self.capacidad_base < -1 or self.capacidad_base == 0:
            raise ValueError(f"La capacidad base debe ser > 0 o -1 (ilimitado). Recibido: {self.capacidad_base}")
        if self.stock_actual < 0:
            raise ValueError(f"El stock no puede ser negativo. Recibido: {self.stock_actual}")
        if self.stock_actual > self.capacidad_base:
            # Permitimos que el stock supere la BASE si hay bonus activos,
            # pero al crearlo sin config asumimos que no hay bonus.
            pass  # Se validará correctamente en operaciones con config

    # ==========================================
    # CAPACIDAD EFECTIVA (Base + Investigación)
    # ==========================================
    # src/economia/silo.py (modificaciones dentro de la clase Silo)

    def get_capacidad_maxima(self, config: GameConfig | None = None) -> int:
        """
        Devuelve la capacidad real.
        -1 significa capacidad ILIMITADA (ej. tesorería del Palacio).
        """
        if self.capacidad_base == -1:
            return -1  # Sin límite
        bonus = config.get_bonus_silo(self.tipo_recurso.name) if config else 0
        return self.capacidad_base + bonus

    def espacio_disponible(self, config: GameConfig | None = None) -> int:
        """Stock restante. -1 = infinito."""
        maxima = self.get_capacidad_maxima(config)
        if maxima == -1:
            return -1  # Siempre hay espacio
        return max(0, maxima - self.stock_actual)

    def esta_lleno(self, config: GameConfig | None = None) -> bool:
        """Un silo con capacidad -1 NUNCA está lleno."""
        if self.capacidad_base == -1:
            return False
        return self.espacio_disponible(config) == 0

    def esta_vacio(self) -> bool:
        return self.stock_actual == 0

    # ==========================================
    # OPERACIONES SEGURA DE STOCK
    # ==========================================
    def agregar(self, cantidad: int, config: GameConfig) -> tuple[bool, int, str]:
        """
        Intenta añadir recursos al silo respetando la capacidad máxima.

        Returns:
            (éxito, cantidad_real_agregada, mensaje)
            - éxito=True: todo o parte se agregó
            - éxito=False: no se pudo agregar nada (cantidad inválida)
        """
        if cantidad <= 0:
            return False, 0, "❌ La cantidad debe ser positiva."

        # Capacidad ilimitada: siempre acepta todo
        if self.capacidad_base == -1:
            self.stock_actual += cantidad
            return True, cantidad, f"✅ {cantidad} unidades de {self.tipo_recurso.value} agregadas."

        disponible = self.espacio_disponible(config)
        if disponible == 0:
            return False, 0, f"❌ {self.nombre} está lleno ({self.get_capacidad_maxima(config)})."

        real = min(cantidad, disponible)
        self.stock_actual += real

        if real < cantidad:
            return True, real, (f"⚠️ Solo se agregaron {real}/{cantidad}. "
                                f"Faltó espacio para {cantidad - real}.")
        return True, real, f"✅ {real} unidades de {self.tipo_recurso.value} agregadas."

    def retirar(self, cantidad: int) -> tuple[bool, int, str]:
        """
        Intenta retirar recursos del silo.
        NOTA: No necesita GameConfig porque retirar nunca excede capacidad.

        Returns:
            (éxito, cantidad_real_retirada, mensaje)
        """
        if cantidad <= 0:
            return False, 0, "❌ La cantidad debe ser positiva."

        if self.stock_actual == 0:
            return False, 0, f"❌ {self.nombre} está vacío."

        real = min(cantidad, self.stock_actual)
        self.stock_actual -= real

        if real < cantidad:
            return True, real, (f"⚠️ Solo se retiraron {real}/{cantidad}. "
                                f"Solo había {self.stock_actual + real} disponibles.")
        return True, real, f"✅ {real} unidades de {self.tipo_recurso.value} retiradas."

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        return (f"📦 {self.nombre} [{self.tipo_recurso.value}] "
                f"{self.stock_actual}/{self.capacidad_base}")
