# src/economia/edificios/laboratorio.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config.game_config import GameConfig
    from src.economia.edificios.palacio import Palacio
    from src.investigacion.arbol_investigaciones import ArbolInvestigaciones


@dataclass
class InvestigacionEnCurso:
    """Representa una tecnología siendo investigada actualmente."""

    tech_id: str
    turnos_restantes: int
    coste_oro_total: int
    oro_pagado: bool = False


@dataclass
class Laboratorio:
    """
    Edificio único del Reino donde se investigan tecnologías.

    Gestiona una cola de investigación secuencial.
    Cada tick del servidor avanza la investigación activa.
    Al completar, emite evento para que el ControladorPartida aplique efectos.
    """

    # ==========================================
    # IDENTIDAD
    # ==========================================
    nombre: str = "Laboratorio Real"
    nivel: int = 1  # Futuro: acelera investigación o aumenta cola

    # ==========================================
    # ESTADO DE INVESTIGACIÓN
    # ==========================================
    cola: list[InvestigacionEnCurso] = field(default_factory=list)
    _max_cola: int = 5

    # ==========================================
    # GESTIÓN DE COLA
    # ==========================================
    def agregar_investigacion(
        self,
        tech_id: str,
        arbol: ArbolInvestigaciones,
        palacio: Palacio,
        config: GameConfig,
        investigaciones_completadas: set[str],
    ) -> tuple[bool, str]:
        """
        Añade una tecnología a la cola de investigación.

        Valida prerequisitos, oro disponible y espacio en cola.
        Descuenta el oro inmediatamente al aceptar.
        """
        if len(self.cola) >= self._max_cola:
            return False, f"❌ Cola llena ({len(self.cola)}/{self._max_cola})."

        puede, razon = arbol.puede_investigar(tech_id, investigaciones_completadas)
        if not puede:
            return False, razon

        tech = arbol.obtener(tech_id)

        oro_actual = palacio.get_oro()
        if oro_actual < tech.coste_oro:
            return False, (
                f"❌ Oro insuficiente para '{tech.nombre}'. "
                f"Necesitas {tech.coste_oro}, tienes {oro_actual}."
            )

        exito, _, msg_oro = palacio.gastar_oro(tech.coste_oro)
        if not exito:
            return False, f"❌ Error al pagar: {msg_oro}"

        self.cola.append(
            InvestigacionEnCurso(
                tech_id=tech_id,
                turnos_restantes=tech.turnos_requeridos,
                coste_oro_total=tech.coste_oro,
                oro_pagado=True,
            )
        )

        pos = len(self.cola)
        return True, (
            f"🔬 '{tech.nombre}' añadida a cola (posición {pos}). "
            f"Coste: {tech.coste_oro} oro | Tiempo: {tech.turnos_requeridos}t."
        )

    def cancelar_investigacion(
        self,
        posicion: int,
        palacio: Palacio,
        arbol: ArbolInvestigaciones,
        config: GameConfig,
    ) -> tuple[bool, str]:
        """
        Cancela una investigación de la cola y reembolsa el oro.
        Posición 0 = investigación activa.
        """
        if not 0 <= posicion < len(self.cola):
            return False, f"❌ Posición inválida. Cola tiene {len(self.cola)} elementos."

        item = self.cola.pop(posicion)

        if item.oro_pagado:
            palacio.recaudar_oro(item.coste_oro_total, config)

        tech = arbol.get(item.tech_id)
        nombre = tech.nombre if tech else item.tech_id
        return True, f"🚫 '{nombre}' cancelada. Oro reembolsado: {item.coste_oro_total}."

    # ==========================================
    # CICLO DE INVESTIGACIÓN (Llamado por Server Tick)
    # ==========================================
    def avanzar_tick(self) -> tuple[bool, str | None]:
        """
        Avanza la investigación activa un turno.

        Returns:
            (completada, tech_id_o_None)
        """
        if not self.cola:
            return False, None

        activa = self.cola[0]
        activa.turnos_restantes -= 1

        if activa.turnos_restantes <= 0:
            self.cola.pop(0)
            return True, activa.tech_id

        return False, None

    # ==========================================
    # CONSULTAS
    # ==========================================
    @property
    def investigacion_activa(self) -> InvestigacionEnCurso | None:
        return self.cola[0] if self.cola else None

    @property
    def esta_investigando(self) -> bool:
        return len(self.cola) > 0

    @property
    def espacios_disponibles(self) -> int:
        return max(0, self._max_cola - len(self.cola))

    def resumen(self, arbol: ArbolInvestigaciones) -> dict:
        """Resumen completo del laboratorio para UI / API."""
        items: list[dict] = []
        for i, item in enumerate(self.cola):
            tech = arbol.get(item.tech_id)
            items.append(
                {
                    "posicion": i,
                    "tech_id": item.tech_id,
                    "nombre": tech.nombre if tech else item.tech_id,
                    "turnos_restantes": item.turnos_restantes,
                    "coste_oro": item.coste_oro_total,
                    "es_activa": i == 0,
                }
            )

        return {
            "nombre": self.nombre,
            "nivel": self.nivel,
            "cola": items,
            "espacios_disponibles": self.espacios_disponibles,
            "max_cola": self._max_cola,
        }

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        if not self.cola:
            return f"🔬 {self.nombre} (Nv.{self.nivel}) | Inactivo"
        activa = self.cola[0]
        return (
            f"🔬 {self.nombre} (Nv.{self.nivel}) | "
            f"Activa: {activa.tech_id} ({activa.turnos_restantes}t) | "
            f"Cola: {len(self.cola)}/{self._max_cola}"
        )
