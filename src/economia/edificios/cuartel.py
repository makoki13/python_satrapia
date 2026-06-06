# src/economia/edificios/cuartel.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.economia.almacen import Almacen
from src.economia.silo import Silo, TipoRecurso

if TYPE_CHECKING:
    from src.config.game_config import GameConfig


# Tropas disponibles desde el inicio (sin investigación)
TROPAS_BASE: list[TipoRecurso] = [TipoRecurso.INFANTERIA]

# Mapeo de tipo de tropa → clave de investigación en GameConfig
CLAVES_INVESTIGACION_TROPA: dict[TipoRecurso, str] = {
    TipoRecurso.CABALLERIA: "tropas_caballeria",
    TipoRecurso.ARQUEROS: "tropas_arqueros",
    TipoRecurso.LANCEROS: "tropas_lanceros",
    TipoRecurso.MAQUINAS_ASALTO: "tropas_maquinas_asalto",
    TipoRecurso.OFICIALES: "tropas_oficiales",
}


@dataclass
class Cuartel:
    """
    Edificio militar donde se reclutan y almacenan tropas.

    - Infantería: siempre disponible (silo creado automáticamente).
    - Resto de tropas: silo creado solo cuando se investiga la tecnología.
    - Las tropas se almacenan en un almacén INTERNO del cuartel.
    - Reclutar consume recursos del almacén de la CIUDAD.
    """

    # ==========================================
    # IDENTIDAD
    # ==========================================
    nombre: str = "Cuartel"

    # ==========================================
    # ALMACÉN INTERNO DE TROPAS
    # ==========================================
    _almacen_tropas: Almacen = field(default=None)  # type: ignore[assignment]

    # ==========================================
    # INICIALIZACIÓN
    # ==========================================
    def __post_init__(self):
        if self._almacen_tropas is None:
            self._almacen_tropas = Almacen(nombre=f"Guarnición de {self.nombre}")
            # La infantería SIEMPRE está disponible
            self._crear_silo_tropa(TipoRecurso.INFANTERIA)

    # ==========================================
    # GESTIÓN DE SILOS POR INVESTIGACIÓN
    # ==========================================
    def _crear_silo_tropa(self, tipo: TipoRecurso) -> bool:
        """Crea un silo para un tipo de tropa. Devuelve False si ya existe."""
        if self._almacen_tropas.tiene_silo_de(tipo):
            return False
        silo = Silo(
            nombre=f"Compañía de {tipo.value}",
            tipo_recurso=tipo,
            capacidad_base=1_000,  # Capacidad base por tipo de tropa
        )
        self._almacen_tropas.agregar_silo(silo)
        return True

    def desbloquear_tropa(self, tipo: TipoRecurso) -> tuple[bool, str]:
        """
        Crea el silo para un nuevo tipo de tropa tras investigar la tecnología.
        Llamado por el Laboratorio o el sistema de investigaciones.
        """
        if tipo in TROPAS_BASE:
            return False, f"ℹ️ {tipo.value} ya está disponible desde el inicio."

        if tipo not in CLAVES_INVESTIGACION_TROPA:
            return False, f"❌ Tipo de tropa desconocido: {tipo.value}"

        creado = self._crear_silo_tropa(tipo)
        if not creado:
            return False, f"ℹ️ {tipo.value} ya estaba desbloqueada."

        return True, f"⚔️ ¡{tipo.value} desbloqueada en {self.nombre}!"

    def tropas_disponibles(self) -> list[TipoRecurso]:
        """Lista de tipos de tropa que tienen silo activo en este cuartel."""
        return self._almacen_tropas.tipos_disponibles

    # ==========================================
    # RECLUTAMIENTO
    # ==========================================
    def reclutar(  # noqa: C901
        self,
        tipo: TipoRecurso,
        cantidad: int,
        almacen_ciudad: Almacen,
        config: GameConfig,
    ) -> tuple[bool, int, str]:
        """
        Recluta tropas: consume recursos de la ciudad y genera unidades
        en el silo correspondiente del cuartel.

        Args:
            tipo: Tipo de tropa a reclutar.
            cantidad: Número de unidades deseado.
            almacen_ciudad: Almacén de la ciudad de donde se consumen recursos.
            config: Configuración global (costes, bonus...).

        Returns:
            (éxito, unidades_reclutadas, mensaje)
        """
        if cantidad <= 0:
            return False, 0, "❌ La cantidad debe ser positiva."

        # Verificar que la tropa está desbloqueada
        if not self._almacen_tropas.tiene_silo_de(tipo):
            return False, 0, f"❌ {tipo.value} no está investigada/disponible."

        # Obtener coste de reclutamiento desde GameConfig
        coste = config.get_coste_reclutamiento(tipo.name)
        if coste is None:
            return False, 0, f"❌ No hay coste definido para {tipo.value}."

        # Calcular recursos necesarios
        recursos_necesarios: dict[str, int] = {}
        for recurso, cantidad_por_unidad in coste.items():
            recursos_necesarios[recurso] = cantidad_por_unidad * cantidad

        # Verificar disponibilidad en el almacén de la ciudad
        for recurso_nombre, cant_nec in recursos_necesarios.items():
            tipo_recurso = TipoRecurso(recurso_nombre)
            stock = almacen_ciudad.stock_total(tipo_recurso)
            if stock < cant_nec:
                return False, 0, (
                    f"❌ Recursos insuficientes para {cantidad} {tipo.value}. "
                    f"Falta {recurso_nombre}: necesitas {cant_nec}, tienes {stock}."
                )

        # Consumir recursos de la ciudad
        for recurso_nombre, cant_nec in recursos_necesarios.items():
            tipo_recurso = TipoRecurso(recurso_nombre)
            almacen_ciudad.retirar_recurso(tipo_recurso, cant_nec)

        # Depositar tropas en el silo del cuartel
        exito, real, msg = self._almacen_tropas.agregar_recurso(tipo, cantidad, config)

        if not exito:
            # Rollback: devolver recursos si no se pudieron almacenar tropas
            for recurso_nombre, cant_nec in recursos_necesarios.items():
                tipo_recurso = TipoRecurso(recurso_nombre)
                almacen_ciudad.agregar_recurso(tipo_recurso, cant_nec, config)
            return False, 0, f"⚠️ Error al almacenar tropas: {msg}"

        if real < cantidad:
            return True, real, (
                f"⚠️ Solo se reclutaron {real}/{cantidad} {tipo.value}. "
                f"Cuartel lleno para este tipo."
            )

        return True, real, f"⚔️ {real} {tipo.value} reclutados en {self.nombre}."

    # ==========================================
    # CONSULTAS
    # ==========================================
    def get_tropas(self, tipo: TipoRecurso) -> int:
        """Devuelve la cantidad de tropas de un tipo almacenadas."""
        return self._almacen_tropas.stock_total(tipo)

    def resumen(self, config: GameConfig) -> dict:
        """Resumen del cuartel para el panel de gestión."""
        tropas: dict[str, dict] = {}
        for tipo in self.tropas_disponibles():
            tropas[tipo.value] = {
                "actual": self.get_tropas(tipo),
                "capacidad": self._almacen_tropas.capacidad_total(tipo, config),
            }
        return {"nombre": self.nombre, "tropas": tropas}

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        num_tipos = len(self.tropas_disponibles())
        total = sum(self.get_tropas(t) for t in self.tropas_disponibles())
        return f"⚔️ {self.nombre} | {num_tipos} tipos | {total} unidades"
