# src/economia/edificios/granja.py
from dataclasses import dataclass

from src.economia.edificio_productivo import EdificioProductivo
from src.economia.fuente_de_recurso import FuenteDeRecurso
from src.economia.silo import TipoRecurso


@dataclass
class Granja(EdificioProductivo):
    """Produce comida desde tierras de cultivo inagotables."""

    @property
    def tipo_recurso(self) -> TipoRecurso:
        return TipoRecurso.COMIDA

    @property
    def produccion_base(self) -> int:
        return 10

    @classmethod
    def crear(cls, nombre: str, nivel: int = 1) -> "Granja":
        fuente = FuenteDeRecurso(
            nombre=f"Tierras de {nombre}",
            nivel=nivel,
            valor_inicial=999_999,
            es_inagotable=True,
        )
        return cls(nombre=nombre, nivel=nivel, fuente=fuente)
