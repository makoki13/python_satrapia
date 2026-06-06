# src/economia/edificio_productivo.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.economia.silo import TipoRecurso

if TYPE_CHECKING:
    from src.config.game_config import GameConfig
    from src.economia.almacen import Almacen
    from src.economia.fuente_de_recurso import FuenteDeRecurso


@dataclass
class EdificioProductivo(ABC):
    """
    Clase base abstracta para todos los edificios que generan recursos.

    Ciclo de producción:
    1. Verifica que la fuente no esté agotada (si tiene fuente finita).
    2. Calcula la cantidad a producir según nivel + investigación.
    3. Extrae esa cantidad de la fuente (consume stock si es finita).
    4. Deposita lo extraído en el almacén de la ciudad.

    Subclases concretas solo definen: tipo_recurso y produccion_base.
    """

    # ==========================================
    # IDENTIDAD Y ESTADO
    # ==========================================
    nombre: str
    nivel: int = 1
    fuente: FuenteDeRecurso | None = None  # None = producción sin fuente directa

    # ==========================================
    # PROPIEDADES ABSTRACTAS (Definidas por subclases)
    # ==========================================
    @property
    @abstractmethod
    def tipo_recurso(self) -> TipoRecurso:
        """Tipo de recurso que produce este edificio."""
        ...

    @property
    @abstractmethod
    def produccion_base(self) -> int:
        """Producción base por turno en el nivel 1."""
        ...

    # ==========================================
    # CÁLCULO DE PRODUCCIÓN
    # ==========================================
    def calcular_produccion(self, config: GameConfig) -> int:
        """
        Calcula la producción teórica del turno actual.
        Fórmula: produccion_base * nivel + bonus_investigacion
        NOTA: Esto es lo que INTENTA producir. Lo real depende de la fuente.
        """
        base = self.produccion_base * self.nivel
        bonus = config.get_bonus_produccion(self.tipo_recurso.name)
        return max(0, base + bonus)

    # ==========================================
    # CICLO DE PRODUCCIÓN COMPLETO
    # ==========================================
    def producir(self, almacen: Almacen, config: GameConfig) -> tuple[bool, int, str]:
        """
        Ejecuta el ciclo completo: verificar fuente → extraer → depositar.

        Returns:
            (éxito, cantidad_depositada, mensaje)
        """
        if self.nivel <= 0:
            return False, 0, f"❌ {self.nombre} tiene nivel inválido ({self.nivel})."

        # PASO 1: Verificar estado de la fuente
        if self.fuente is not None and self.fuente.esta_agotada():
            return False, 0, f"⛔ {self.nombre}: fuente agotada. Producción detenida."

        # PASO 2: Calcular cuánto se quiere producir
        cantidad_deseada = self.calcular_produccion(config)
        if cantidad_deseada == 0:
            return True, 0, f"ℹ️ {self.nombre} no produjo nada este turno."

        # PASO 3: Extraer de la fuente (limita la cantidad real si es finita)
        if self.fuente is not None:
            exito_ext, cantidad_real, msg_ext = self.fuente.extraer(cantidad_deseada)
            if not exito_ext:
                return False, 0, f"⚠️ {self.nombre}: {msg_ext}"
            # Si la fuente es inagotable, cantidad_real == cantidad_deseada siempre
            # Si es finita y queda poco, cantidad_real < cantidad_deseada
        else:
            # Sin fuente asociada: producción directa (casos especiales)
            cantidad_real = cantidad_deseada

        # PASO 4: Depositar en el almacén
        exito_dep, depositado, msg_dep = almacen.agregar_recurso(
            self.tipo_recurso, cantidad_real, config
        )

        if not exito_dep:
            return False, 0, f"⚠️ {self.nombre}: {msg_dep}"

        # Mensaje compuesto si hubo pérdida en cualquier etapa
        if depositado < cantidad_real:
            perdida_almacen = cantidad_real - depositado
            return True, depositado, (
                f"⚠️ {self.nombre}: se extrajeron {cantidad_real} pero solo se almacenaron "
                f"{depositado}. Se perdieron {perdida_almacen} por falta de espacio."
            )

        if cantidad_real < cantidad_deseada:
            return True, depositado, (
                f"⚠️ {self.nombre}: produjo {depositado}/{cantidad_deseada} "
                f"(fuente con stock limitado)."
            )

        return True, depositado, f"✅ {self.nombre} depositó {depositado} de {self.tipo_recurso.value}."

    # ==========================================
    # MEJORAS
    # ==========================================
    def mejorar(self) -> tuple[bool, str]:
        """Sube el nivel del edificio en 1."""
        self.nivel += 1
        return True, f"⬆️ {self.nombre} mejorado a nivel {self.nivel}."

    # ==========================================
    # CONSULTAS PARA EL PANEL DE GESTIÓN
    # ==========================================
    def estado_fuente(self) -> str:
        """Devuelve un string descriptivo del estado de la fuente."""
        if self.fuente is None:
            return "Sin fuente asociada"
        if self.fuente.es_inagotable:
            return "♻️ Inagotable"
        if self.fuente.esta_agotada():
            return "⛔ AGOTADA"
        return f"⛏️ {self.fuente.porcentaje_restante():.0f}% restante"

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        fuente_info = self.estado_fuente()
        return f"🏭 {self.nombre} (Nv.{self.nivel}) → {self.tipo_recurso.value} [{fuente_info}]"
