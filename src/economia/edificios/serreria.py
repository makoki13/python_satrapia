# src/economia/edificios/serreria.py
from __future__ import annotations

from dataclasses import dataclass

from src.core.coordenada import Coordenada
from src.economia.almacen import Almacen
from src.economia.edificio_productivo import EdificioProductivo
from src.economia.fuente_de_recurso import FuenteDeRecurso
from src.economia.silo import Silo, TipoRecurso


@dataclass
class Serreria(EdificioProductivo):
    """
    Produce madera desde bosques inagotables.

    Análoga a la granja pero con recurso MADERA:
    - Posición propia en el mapa (distinta de la ciudad)
    - Almacén local con un único silo de madera
    - Disparador automático de transporte cuando el silo se llena
    """

    coordenada: Coordenada | None = None
    almacen: Almacen | None = None

    @property
    def tipo_recurso(self) -> TipoRecurso:
        return TipoRecurso.MADERA

    @property
    def produccion_base(self) -> int:
        return 10  # Igual que granja para sincronizar ciclos de transporte

    @classmethod
    def crear(
        cls,
        nombre: str,
        nivel: int = 1,
        coordenada: Coordenada | None = None,
        capacidad_silo: int = 100,
    ) -> Serreria:
        """Crea una serrería con fuente inagotable, coordenada y almacén local."""
        fuente = FuenteDeRecurso(
            nombre=f"Bosques de {nombre}",
            nivel=nivel,
            valor_inicial=999_999,
            es_inagotable=True,
        )

        alm = Almacen(nombre=f"Almacén {nombre}")
        alm.agregar_silo(Silo(
            nombre=f"Silo Madera {nombre}",
            tipo_recurso=TipoRecurso.MADERA,
            capacidad_base=capacidad_silo,
        ))

        return cls(
            nombre=nombre,
            nivel=nivel,
            fuente=fuente,
            coordenada=coordenada,
            almacen=alm,
        )
