# src/economia/edificios/mina_hierro.py
from dataclasses import dataclass

from src.economia.edificio_productivo import EdificioProductivo
from src.economia.fuente_de_recurso import FuenteDeRecurso
from src.economia.silo import TipoRecurso


@dataclass
class MinaHierro(EdificioProductivo):
    """Extrae hierro de una veta finita."""

    @property
    def tipo_recurso(self) -> TipoRecurso:
        return TipoRecurso.HIERRO

    @property
    def produccion_base(self) -> int:
        return 5

    @classmethod
    def crear(cls, nombre: str, nivel_edificio: int = 1) -> "MinaHierro":
        fuente = FuenteDeRecurso.crear_con_nivel_aleatorio(
            nombre=f"Veta de Hierro de {nombre}",
            es_inagotable=False,
        )
        return cls(nombre=nombre, nivel=nivel_edificio, fuente=fuente)
