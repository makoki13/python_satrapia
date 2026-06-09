# src/config/parametro_juego.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ContribucionParametro:
    """
    Representa la aportación de una investigación concreta a un parámetro.
    Es inmutable y puramente datos.
    """
    id_investigacion: str  # Ej: "tech_trigo_1", "tech_caballeria_3"
    valor: float           # Cantidad aditiva al porcentaje (ej: 0.10 = +10%)


@dataclass(frozen=True)
class ParametroJuego:
    """
    Parámetro modificable del juego cuyo valor depende de investigaciones completadas.

    Fórmula: valor_actual = valor_maximo * min(1.0, porcentaje_inicial + sum(contribuciones))

    - Tipo NUMÉRICO: Escala progresivamente (velocidad, producción, fuerza...)
    - Tipo LÓGICO: Binario (0 o 1). Desbloquea mecánicas/tropas/edificios.
      Un lógico es simplemente un numérico con max=1.0 e inicial=0.0
    """

    # ==========================================
    # IDENTIDAD
    # ==========================================
    id: str                              # "velocidad_cosecha", "fuerza_lanceros"
    nombre: str                          # Nombre legible para UI
    tipo: Literal["numerico", "logico"]

    # ==========================================
    # CONFIGURACIÓN BASE
    # ==========================================
    valor_maximo: float                  # Valor cuando porcentaje efectivo = 1.0
    porcentaje_inicial: float            # Porcentaje al inicio (0.0 a 1.0)

    # ==========================================
    # CONTRIBUCIONES DE INVESTIGACIONES
    # ==========================================
    # Tuple inmutable: garantiza que nadie modifica contribuciones en runtime
    contribuciones: tuple[ContribucionParametro, ...] = ()

    # ==========================================
    # VALIDACIONES
    # ==========================================
    def __post_init__(self):
        if not 0.0 <= self.porcentaje_inicial <= 1.0:
            raise ValueError(
                f"porcentaje_inicial debe estar entre 0.0 y 1.0. "
                f"Recibido: {self.porcentaje_inicial}"
            )
        if self.valor_maximo < 0:
            raise ValueError(f"valor_maximo no puede ser negativo. Recibido: {self.valor_maximo}")
        if self.tipo == "logico":
            if self.valor_maximo != 1.0:
                raise ValueError("Los parámetros lógicos deben tener valor_maximo=1.0")
            if self.porcentaje_inicial != 0.0:
                raise ValueError("Los parámetros lógicos deben tener porcentaje_inicial=0.0")

    # ==========================================
    # PROPIEDADES DERIVADAS
    # ==========================================
    @property
    def es_logico(self) -> bool:
        """Devuelve True si es un parámetro binario (desbloqueo)."""
        return self.tipo == "logico"

    # ==========================================
    # CÁLCULO DE VALOR ACTUAL
    # ==========================================
    def calcular_porcentaje(self, investigaciones_completadas: set[str]) -> float:
        """
        Calcula el porcentaje efectivo (0.0 a 1.0) basado en investigaciones terminadas.
        Siempre acotado entre 0.0 y 1.0.
        """
        suma = sum(
            c.valor for c in self.contribuciones
            if c.id_investigacion in investigaciones_completadas
        )
        return max(0.0, min(1.0, self.porcentaje_inicial + suma))

    def calcular_valor(self, investigaciones_completadas: set[str]) -> float:
        """
        Devuelve el valor actual del parámetro.
        Para lógicos: 0.0 (bloqueado) o 1.0 (desbloqueado).
        Para numéricos: valor_maximo * porcentaje_efectivo.
        """
        return self.valor_maximo * self.calcular_porcentaje(investigaciones_completadas)

    def esta_desbloqueado(self, investigaciones_completadas: set[str]) -> bool:
        """
        Solo relevante para parámetros lógicos.
        Devuelve True si el valor actual >= 1.0.
        Los numéricos siempre retornan True.
        """
        if self.tipo == "numerico":
            return True
        return self.calcular_valor(investigaciones_completadas) >= 1.0

    # ==========================================
    # CONSULTAS PARA UI / DEBUG
    # ==========================================
    def progreso(self, investigaciones_completadas: set[str]) -> dict:
        """Devuelve información detallada para mostrar en el panel de gestión."""
        pct = self.calcular_porcentaje(investigaciones_completadas)
        total_contribuciones = len(self.contribuciones)
        completadas = sum(
            1 for c in self.contribuciones
            if c.id_investigacion in investigaciones_completadas
        )
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "valor_actual": round(self.calcular_valor(investigaciones_completadas), 2),
            "valor_maximo": self.valor_maximo,
            "porcentaje": round(pct * 100, 1),
            "investigaciones": f"{completadas}/{total_contribuciones}",
            "desbloqueado": self.esta_desbloqueado(investigaciones_completadas),
        }

    # ==========================================
    # FACTORY METHODS (Creación limpia)
    # ==========================================
    @classmethod
    def numerico(
        cls,
        id: str,
        nombre: str,
        valor_maximo: float,
        porcentaje_inicial: float,
        contribuciones: list[ContribucionParametro] | None = None,
    ) -> ParametroJuego:
        """Crea un parámetro numérico con validación automática."""
        return cls(
            id=id,
            nombre=nombre,
            tipo="numerico",
            valor_maximo=valor_maximo,
            porcentaje_inicial=porcentaje_inicial,
            contribuciones=tuple(contribuciones or []),
        )

    @classmethod
    def logico(
        cls,
        id: str,
        nombre: str,
        contribuciones: list[ContribucionParametro] | None = None,
    ) -> ParametroJuego:
        """Crea un parámetro lógico (binario) con valores forzados."""
        return cls(
            id=id,
            nombre=nombre,
            tipo="logico",
            valor_maximo=1.0,
            porcentaje_inicial=0.0,
            contribuciones=tuple(contribuciones or []),
        )

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        icono = "🔢" if self.tipo == "numerico" else "🔒"
        return f"{icono} {self.nombre} (max={self.valor_maximo}, ini={self.porcentaje_inicial:.0%})"
