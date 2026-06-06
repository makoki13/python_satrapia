# src/economia/edificios/cantera.py
from dataclasses import dataclass

from src.economia.edificio_productivo import EdificioProductivo
from src.economia.fuente_de_recurso import FuenteDeRecurso
from src.economia.silo import TipoRecurso


@dataclass
class Cantera(EdificioProductivo):
    """Extrae piedra de un yacimiento finito."""

    @property
    def tipo_recurso(self) -> TipoRecurso:
        return TipoRecurso.PIEDRA

    @property
    def produccion_base(self) -> int:
        return 6

    @classmethod
    def crear(cls, nombre: str, nivel_edificio: int = 1) -> "Cantera":
        fuente = FuenteDeRecurso.crear_con_nivel_aleatorio(
            nombre=f"Cantera de {nombre}",
            es_inagotable=False,
        )
        return cls(nombre=nombre, nivel=nivel_edificio, fuente=fuente)
