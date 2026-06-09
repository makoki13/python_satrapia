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
    oro_pagado: bool = False  # True si el oro ya fue descontado al iniciar


@dataclass
class Laboratorio:
    """
    Edificio urbano donde se investigan tecnologías.

    Gestiona una cola de investigación secuencial.
    Cada tick del servidor avanza la investigación activa.
    Al completar, emite evento para que el ControladorPartida aplique efectos.
    """

    # ==========================================
    # IDENTIDAD
    # ==========================================
    nombre: str = "Laboratorio"
    nivel: int = 1  # Nivel del laboratorio (futuro: acelera investigación)

    # ==========================================
    # ESTADO DE INVESTIGACIÓN
    # ==========================================
    cola: list[InvestigacionEnCurso] = field(default_factory=list)
    _max_cola: int = 5  # Máximo de investigaciones en cola

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

        Valida: prerequisitos, oro disponible, espacio en cola.
        Descuenta el oro inmediatamente al aceptar.
        """
        # Validar espacio en cola
        if len(self.cola) >= self._max_cola:
            return False, f"❌ Cola llena ({self._max_cola}/{self._max_cola})."

        # Validar que existe y está disponible
        puede, razon = arbol.puede_investigar(tech_id, investigaciones_completadas)
        if not puede:
            return False, razon

        tech = arbol.obtener(tech_id)

        # Validar oro suficiente
        oro_actual = palacio.get_oro()
        if oro_actual < tech.coste_oro:
            return False, (
                f"❌ Oro insuficiente para '{tech.nombre}'. "
                f"Necesitas {tech.coste_oro}, tienes {oro_actual}."
            )

        # Descontar oro inmediatamente
        exito, _, msg_oro = palacio.gastar_oro(tech.coste_oro)
        if not exito:
            return False, f"❌ Error al pagar: {msg_oro}"

        # Añadir a cola
        self.cola.append(InvestigacionEnCurso(
            tech_id=tech_id,
            turnos_restantes=tech.turnos_requeridos,
            coste_oro_total=tech.coste_oro,
            oro_pagado=True,
        ))

        pos = len(self.cola)
        return True, (
            f"🔬 '{tech.nombre}' añadida a cola (posición {pos}). "
            f"Coste: {tech.coste_oro} oro | Tiempo: {tech.turnos_requeridos} turnos."
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

        # Reembolsar oro
        if item.oro_pagado:
            from src.config.game_config import GameConfig
            # Usamos config dummy porque recaudar_oro lo necesita pero no usa bonus para oro
            # En producción, pasar el config real desde el controlador
            palacio.recaudar_oro(item.coste_oro_total, None)  # type: ignore[arg-type]

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
            (completada, tech_id_completado_o_None)
            Si completada=True, el ControladorPartida debe aplicar efectos
            y mover la tech a investigaciones_completadas.
        """
        if not self.cola:
            return False, None

        activa = self.cola[0]
        activa.turnos_restantes -= 1

        if activa.turnos_restantes <= 0:
            # Investigación completada
            self.cola.pop(0)
            return True, activa.tech_id

        return False, None

    # ==========================================
    # CONSULTAS
    # ==========================================
    @property
    def investigacion_activa(self) -> InvestigacionEnCurso | None:
        """Devuelve la investigación en curso (primera de la cola) o None."""
        return self.cola[0] if self.cola else None

    @property
    def esta_investigando(self) -> bool:
        return len(self.cola) > 0

    @property
    def espacios_disponibles(self) -> int:
        return max(0, self._max_cola - len(self.cola))

    def resumen(
        self,
        arbol: ArbolInvestigaciones,
        config: GameConfig,
    ) -> dict:
        """Resumen completo del laboratorio para la UI / API."""
        items: list[dict] = []
        for i, item in enumerate(self.cola):
            tech = arbol.get(item.tech_id)
            items.append({
                "posicion": i,
                "tech_id": item.tech_id,
                "nombre": tech.nombre if tech else item.tech_id,
                "turnos_restantes": item.turnos_restantes,
                "coste_oro": item.coste_oro_total,
                "es_activa": i == 0,
            })

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
