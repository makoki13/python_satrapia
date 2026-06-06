# src/economia/edificios/mina_oro.py
from dataclasses import dataclass

from src.economia.edificio_productivo import EdificioProductivo
from src.economia.fuente_de_recurso import FuenteDeRecurso
from src.economia.silo import TipoRecurso


@dataclass
class MinaOro(EdificioProductivo):
    """Extrae oro de una veta finita. Recurso estratégico para la tesorería."""

    @property
    def tipo_recurso(self) -> TipoRecurso:
        return TipoRecurso.ORO

    @property
    def produccion_base(self) -> int:
        return 3

    @classmethod
    def crear(cls, nombre: str, nivel_edificio: int = 1) -> "MinaOro":
        fuente = FuenteDeRecurso.crear_con_nivel_aleatorio(
            nombre=f"Veta de Oro de {nombre}",
            es_inagotable=False,
        )
        return cls(nombre=nombre, nivel=nivel_edificio, fuente=fuente)
