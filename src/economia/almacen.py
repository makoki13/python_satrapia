# src/economia/almacen.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.economia.silo import Silo, TipoRecurso

if TYPE_CHECKING:
    from src.config.game_config import GameConfig


@dataclass
class Almacen:
    """
    Contenedor genérico de recursos compuesto por Silos únicos por tipo.

    Restricción: máximo 1 silo por TipoRecurso.
    Es agnóstico al contexto: lo usan ciudades, ejércitos y caravanas por igual.
    """

    # ==========================================
    # IDENTIDAD
    # ==========================================
    nombre: str

    # ==========================================
    # COLECCIÓN DE SILOS (1:1 por tipo de recurso)
    # ==========================================
    # Clave = TipoRecurso, Valor = Silo (único)
    _silos: dict[TipoRecurso, Silo] = field(default_factory=dict)

    # ==========================================
    # GESTIÓN DE SILOS
    # ==========================================
    def agregar_silo(self, silo: Silo) -> tuple[bool, str]:
        """
        Añade un silo al almacén.
        Rechaza la operación si ya existe un silo para ese tipo de recurso.
        """
        if silo.tipo_recurso in self._silos:
            return False, (f"❌ Ya existe un silo de {silo.tipo_recurso.value} "
                           f"en {self.nombre}. No se permiten duplicados.")
        self._silos[silo.tipo_recurso] = silo
        return True, f"✅ Silo de {silo.tipo_recurso.value} añadido a {self.nombre}."

    def eliminar_silo(self, tipo: TipoRecurso) -> bool:
        """Elimina el silo de un tipo de recurso. Devuelve False si no existía."""
        return self._silos.pop(tipo, None) is not None

    def obtener_silo(self, tipo: TipoRecurso) -> Silo | None:
        """Devuelve el silo de un tipo específico, o None si no existe."""
        return self._silos.get(tipo)

    def tiene_silo_de(self, tipo: TipoRecurso) -> bool:
        """Verifica si existe un silo para el recurso indicado."""
        return tipo in self._silos

    @property
    def num_silos(self) -> int:
        """Número total de silos en el almacén."""
        return len(self._silos)

    @property
    def tipos_disponibles(self) -> list[TipoRecurso]:
        """Lista de tipos de recurso que tienen silo asignado."""
        return list(self._silos.keys())

    # ==========================================
    # OPERACIONES DE STOCK (Directas, sin distribución)
    # ==========================================
    def agregar_recurso(
        self, tipo: TipoRecurso, cantidad: int, config: GameConfig
    ) -> tuple[bool, int, str]:
        """
        Intenta añadir recursos al silo correspondiente.
        Como solo hay 1 silo por tipo, la operación es directa.
        """
        if cantidad <= 0:
            return False, 0, "❌ La cantidad debe ser positiva."

        silo = self._silos.get(tipo)
        if silo is None:
            return False, 0, f"❌ No hay silo para {tipo.value} en {self.nombre}."

        return silo.agregar(cantidad, config)

    def retirar_recurso(
        self, tipo: TipoRecurso, cantidad: int
    ) -> tuple[bool, int, str]:
        """
        Intenta retirar recursos del silo correspondiente.
        Como solo hay 1 silo por tipo, la operación es directa.
        """
        if cantidad <= 0:
            return False, 0, "❌ La cantidad debe ser positiva."

        silo = self._silos.get(tipo)
        if silo is None:
            return False, 0, f"❌ No hay silo para {tipo.value} en {self.nombre}."

        return silo.retirar(cantidad)

    # ==========================================
    # CONSULTAS DE ESTADO
    # ==========================================
    def stock_total(self, tipo: TipoRecurso) -> int:
        """Devuelve el stock del silo de ese tipo (0 si no existe)."""
        silo = self._silos.get(tipo)
        return silo.stock_actual if silo else 0

    def capacidad_total(self, tipo: TipoRecurso, config: GameConfig) -> int:
        """Devuelve la capacidad efectiva del silo de ese tipo (0 si no existe)."""
        silo = self._silos.get(tipo)
        return silo.get_capacidad_maxima(config) if silo else 0

    def resumen_stock(self, config: GameConfig) -> dict[str, dict]:
        """
        Resumen completo del almacén para el panel de gestión / API.
        Formato: {"Comida": {"stock": 150, "capacidad": 300}, ...}
        """
        resumen: dict[str, dict] = {}
        for tipo, silo in self._silos.items():
            resumen[tipo.value] = {
                "stock": silo.stock_actual,
                "capacidad": silo.get_capacidad_maxima(config),
            }
        return resumen

    @property
    def silos_items(self) -> list[tuple[TipoRecurso, Silo]]:
        """
        Devuelve lista de tuplas (tipo_recurso, silo) para iteración externa.
        Útil para disparadores automáticos y análisis logístico.
        """
        return list(self._silos.items())

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        tipos = ", ".join(t.value for t in self._silos) or "vacío"
        return f"🏪 {self.nombre} ({self.num_silos} silos: {tipos})"
