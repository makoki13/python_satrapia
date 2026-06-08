# src/investigacion/tecnologia.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EfectoTecnologia:
    """
    Vincula una tecnología con un parámetro del juego.
    Es puramente dato: dice QUÉ parámetro modificar y CUÁNTO.
    """
    id_parametro: str   # "prod_comida_granja", "tropas_caballeria_disponible"
    valor: float        # Contribución aditiva al porcentaje del parámetro


@dataclass(frozen=True)
class Tecnologia:
    """
    Nodo del árbol de investigaciones.

    Jerarquía: Bloque (1-7) → Subrama (1-7) → Nivel (1-7)
    Cada nivel N requiere haber completado el nivel N-1 de la misma subrama.
    Nivel 1 siempre disponible (padre_id = None).

    Al completarse, aplica sus efectos a los ParametroJuego correspondientes.
    """

    # ==========================================
    # IDENTIDAD Y POSICIÓN EN EL ÁRBOL
    # ==========================================
    id: str                     # "1.1.1_regadio_inundacion" - estable para siempre
    nombre: str                 # "Regadío por inundación" - visible al jugador
    bloque: int                 # 1-7 (bloque temático)
    subrama: int                # 1-7 (subrama dentro del bloque)
    nivel: int                  # 1-7 (posición en la cadena lineal)
    padre_id: str | None        # None si nivel==1; else id del nivel anterior

    # ==========================================
    # COSTES
    # ==========================================
    coste_oro: int              # Oro necesario para investigar
    turnos_requeridos: int      # Turnos en el Laboratorio

    # ==========================================
    # EFECTOS (Vínculo con ParametroJuego)
    # ==========================================
    # Tuple inmutable: una tecnología puede afectar a múltiples parámetros
    efectos: tuple[EfectoTecnologia, ...] = ()

    # ==========================================
    # DESCRIPCIÓN
    # ==========================================
    descripcion: str = ""       # Texto para tooltip / panel de investigación

    # ==========================================
    # VALIDACIONES
    # ==========================================
    def __post_init__(self):
        if not 1 <= self.bloque <= 7:
            raise ValueError(f"bloque debe ser 1-7. Recibido: {self.bloque}")
        if not 1 <= self.subrama <= 7:
            raise ValueError(f"subrama debe ser 1-7. Recibido: {self.subrama}")
        if not 1 <= self.nivel <= 7:
            raise ValueError(f"nivel debe ser 1-7. Recibido: {self.nivel}")
        if self.coste_oro < 0:
            raise ValueError(f"coste_oro no puede ser negativo. Recibido: {self.coste_oro}")
        if self.turnos_requeridos <= 0:
            raise ValueError(f"turnos_requeridos debe ser > 0. Recibido: {self.turnos_requeridos}")

        # Nivel 1 NO tiene padre; niveles 2-7 SÍ deben tenerlo
        if self.nivel == 1 and self.padre_id is not None:
            raise ValueError(f"Tecnología de nivel 1 no debe tener padre_id. Recibido: {self.padre_id}")
        if self.nivel > 1 and self.padre_id is None:
            raise ValueError(f"Tecnología de nivel {self.nivel} debe tener padre_id.")

    # ==========================================
    # CONSULTAS
    # ==========================================
    @property
    def es_nivel_1(self) -> bool:
        """Las tecnologías de nivel 1 siempre están disponibles."""
        return self.nivel == 1

    def afecta_a_parametro(self, id_parametro: str) -> bool:
        """Verifica si esta tecnología modifica un parámetro específico."""
        return any(e.id_parametro == id_parametro for e in self.efectos)

    def get_contribucion(self, id_parametro: str) -> float:
        """Devuelve la contribución total a un parámetro (suma si hay múltiples efectos)."""
        return sum(e.valor for e in self.efectos if e.id_parametro == id_parametro)

    # ==========================================
    # FACTORY METHOD (Creación con costes escalados)
    # ==========================================
    @classmethod
    def crear(
        cls,
        id: str,
        nombre: str,
        bloque: int,
        subrama: int,
        nivel: int,
        padre_id: str | None,
        efectos: list[EfectoTecnologia] | None = None,
        descripcion: str = "",
        coste_oro_base: int = 100,
        turnos_base: int = 3,
    ) -> Tecnologia:
        """
        Crea una tecnología con costes escalados automáticamente por nivel.

        Escala recomendada:
          Nivel 1: ×1 oro, ×1 turnos
          Nivel 2: ×3 oro, ×2 turnos
          Nivel 3: ×8 oro, ×3 turnos
          Nivel 4: ×15 oro, ×5 turnos
          Nivel 5: ×25 oro, ×7 turnos
          Nivel 6: ×40 oro, ×10 turnos
          Nivel 7: ×60 oro, ×15 turnos
        """
        multiplicadores_oro = {1: 1, 2: 3, 3: 8, 4: 15, 5: 25, 6: 40, 7: 60}
        multiplicadores_turnos = {1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 10, 7: 15}

        return cls(
            id=id,
            nombre=nombre,
            bloque=bloque,
            subrama=subrama,
            nivel=nivel,
            padre_id=padre_id,
            coste_oro=coste_oro_base * multiplicadores_oro.get(nivel, 1),
            turnos_requeridos=turnos_base * multiplicadores_turnos.get(nivel, 1),
            efectos=tuple(efectos or []),
            descripcion=descripcion,
        )

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        padre = f" ← {self.padre_id}" if self.padre_id else " (inicio)"
        num_efectos = len(self.efectos)
        return (f"🔬 [{self.bloque}.{self.subrama}.{self.nivel}] {self.nombre} "
                f"| 💰{self.coste_oro} ⏳{self.turnos_requeridos}t "
                f"| {num_efectos} efecto(s){padre}")
