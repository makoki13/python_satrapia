# src/economia/edificios/serreria.py
from dataclasses import dataclass

from src.economia.edificio_productivo import EdificioProductivo
from src.economia.fuente_de_recurso import FuenteDeRecurso
from src.economia.silo import TipoRecurso


@dataclass
class Serreria(EdificioProductivo):
    """Produce madera desde bosques gestionados (inagotable)."""

    @property
    def tipo_recurso(self) -> TipoRecurso:
        return TipoRecurso.MADERA

    @property
    def produccion_base(self) -> int:
        return 8

    @classmethod
    def crear(cls, nombre: str, nivel: int = 1) -> "Serreria":
        fuente = FuenteDeRecurso(
            nombre=f"Bosque de {nombre}",
            nivel=nivel,
            valor_inicial=999_999,
            es_inagotable=True,
        )
        return cls(nombre=nombre, nivel=nivel, fuente=fuente)
