# src/economia/edificios/palacio.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.economia.almacen import Almacen
from src.economia.silo import Silo, TipoRecurso

if TYPE_CHECKING:
    from src.config.game_config import GameConfig


@dataclass
class Palacio:
    """
    Edificio especial único por imperio. Sede del poder imperial.

    Gestiona su propio almacén interno con exactamente 2 silos:
    - POBLACION: Censo de habitantes (crece/decrece por mecánicas)
    - ORO: Tesorería con capacidad ILIMITADA (-1).

    La recaudación de impuestos = población × coeficiente_fijo.
    NO hereda de EdificioProductivo: su lógica es de gestión, no de extracción.
    """

    # ==========================================
    # IDENTIDAD
    # ==========================================
    nombre: str = "Palacio Imperial"

    # ==========================================
    # CONSTANTES DE IMPUESTOS
    # ==========================================
    COEFICIENTE_IMPUESTOS_BASE: float = 0.1  # 10% de la población → oro por turno
    # Futuro: este valor vendrá de GameConfig cuando haya investigaciones fiscales

    # ==========================================
    # ALMACÉN INTERNO (Privado, solo 2 silos)
    # ==========================================
    _almacen_interno: Almacen = field(default=None)  # type: ignore[assignment]

    # ==========================================
    # INICIALIZACIÓN
    # ==========================================
    def __post_init__(self):
        if self._almacen_interno is None:
            self._almacen_interno = Almacen(nombre=f"Tesorería de {self.nombre}")

            # Silo de Población (con límite base)
            silo_poblacion = Silo(
                nombre="Censo de Población",
                tipo_recurso=TipoRecurso.POBLACION,
                capacidad_base=10_000,
            )

            # Silo de Oro (CAPACIDAD ILIMITADA)
            silo_oro = Silo(
                nombre="Tesoro Imperial",
                tipo_recurso=TipoRecurso.ORO,
                capacidad_base=-1,  # -1 = sin límite
            )

            self._almacen_interno.agregar_silo(silo_poblacion)
            self._almacen_interno.agregar_silo(silo_oro)

    # ==========================================
    # GESTIÓN DE POBLACIÓN
    # ==========================================
    def actualizar_poblacion(self, cambio: int) -> tuple[bool, int, str]:
        """
        Modifica la población de la ciudad.
        Positivo = crecimiento. Negativo = decrecimiento.
        """
        if cambio > 0:
            return self._almacen_interno.agregar_recurso(
                TipoRecurso.POBLACION, cambio, config=None  # type: ignore[arg-type]
            )
        elif cambio < 0:
            return self._almacen_interno.retirar_recurso(
                TipoRecurso.POBLACION, abs(cambio)
            )
        return True, 0, "ℹ️ Sin cambio de población."

    def get_poblacion(self) -> int:
        """Devuelve la población actual de la ciudad."""
        return self._almacen_interno.stock_total(TipoRecurso.POBLACION)

    def get_capacidad_poblacion(self, config: GameConfig) -> int:
        """Devuelve el límite máximo de población (base + investigación)."""
        return self._almacen_interno.capacidad_total(TipoRecurso.POBLACION, config)

    # ==========================================
    # GESTIÓN DE ORO (TESORERÍA ILIMITADA)
    # ==========================================
    def recaudar_oro(self, cantidad: int, config: GameConfig) -> tuple[bool, int, str]:
        """Ingresa oro en la tesorería (impuestos, comercio, tributos)."""
        if cantidad <= 0:
            return False, 0, "❌ La cantidad de oro debe ser positiva."
        return self._almacen_interno.agregar_recurso(TipoRecurso.ORO, cantidad, config)

    def gastar_oro(self, cantidad: int) -> tuple[bool, int, str]:
        """Gasta oro de la tesorería (construcción, ejército, diplomacia)."""
        if cantidad <= 0:
            return False, 0, "❌ La cantidad de oro debe ser positiva."
        return self._almacen_interno.retirar_recurso(TipoRecurso.ORO, cantidad)

    def get_oro(self) -> int:
        """Devuelve el oro actual en esta tesorería."""
        return self._almacen_interno.stock_total(TipoRecurso.ORO)

    # ==========================================
    # RECAUDACIÓN DE IMPUESTOS
    # ==========================================
    def calcular_impuestos(self) -> int:
        """
        Calcula los impuestos del turno actual SIN aplicarlos.
        Fórmula: población × coeficiente_fijo (redondeado a entero).
        Útil para mostrar previsión en el panel de gestión.
        """
        poblacion = self.get_poblacion()
        return int(poblacion * self.COEFICIENTE_IMPUESTOS_BASE)

    def recaudar_impuestos(self, config: GameConfig) -> tuple[bool, int, str]:
        """
        Calcula y deposita los impuestos en la tesorería del Palacio.
        El silo de oro es ilimitado, nunca habrá pérdida por overflow.

        Returns:
            (éxito, oro_recaudado, mensaje)
        """
        impuestos = self.calcular_impuestos()

        if impuestos == 0:
            return True, 0, "ℹ️ Sin población, no hay impuestos que recaudar."

        exito, real, msg = self.recaudar_oro(impuestos, config)

        if not exito:
            return False, 0, f"⚠️ Error al recaudar impuestos: {msg}"

        return True, real, f"💰 Impuestos recaudados: {real} oro (de {self.get_poblacion()} hab.)"

    # ==========================================
    # CONSULTAS PARA EL PANEL DE GESTIÓN
    # ==========================================
    def resumen(self, config: GameConfig) -> dict:
        """Resumen completo del Palacio para la UI / API."""
        cap_oro = self._almacen_interno.capacidad_total(TipoRecurso.ORO, config)
        cap_oro_str = "∞" if cap_oro == -1 else str(cap_oro)

        return {
            "nombre": self.nombre,
            "poblacion": {
                "actual": self.get_poblacion(),
                "maxima": self.get_capacidad_poblacion(config),
            },
            "oro": {
                "actual": self.get_oro(),
                "maxima": cap_oro_str,
                "impuestos_previstos": self.calcular_impuestos(),
            },
        }

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        pob = self.get_poblacion()
        oro = self.get_oro()
        return f"🏛️ {self.nombre} | 👥 {pob} hab. | 💰 {oro} oro"
