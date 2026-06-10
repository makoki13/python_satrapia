# src/economia/edificios/granja.py
from __future__ import annotations

from dataclasses import dataclass

from src.core.coordenada import Coordenada
from src.economia.almacen import Almacen
from src.economia.edificio_productivo import EdificioProductivo
from src.economia.fuente_de_recurso import FuenteDeRecurso
from src.economia.silo import Silo, TipoRecurso


@dataclass
class Granja(EdificioProductivo):
    """
    Produce comida desde tierras de cultivo inagotables.

    A diferencia de otros edificios productivos, la granja tiene:
    - Una posición propia en el mapa (diferente de la ciudad a la que pertenece)
    - Un almacén local con un único silo de comida
    - Disparador automático de transporte cuando el silo se llena
    """

    # ==========================================
    # POSICIÓN EN EL MAPA
    # ==========================================
    coordenada: Coordenada | None = None

    # ==========================================
    # ALMACÉN LOCAL CON SILO DE COMIDA
    # ==========================================
    almacen: Almacen | None = None

    # ==========================================
    # PROPIEDADES ABSTRACTAS IMPLEMENTADAS
    # ==========================================
    @property
    def tipo_recurso(self) -> TipoRecurso:
        return TipoRecurso.COMIDA

    @property
    def produccion_base(self) -> int:
        return 10

    # ==========================================
    # FACTORY METHOD
    # ==========================================
    @classmethod
    def crear(
        cls,
        nombre: str,
        nivel: int = 1,
        coordenada: Coordenada | None = None,
        capacidad_silo: int = 100,
    ) -> Granja:
        """
        Crea una granja completamente configurada con fuente inagotable,
        coordenada en el mapa y almacén local con silo de comida.
        """
        fuente = FuenteDeRecurso(
            nombre=f"Tierras de {nombre}",
            nivel=nivel,
            valor_inicial=999_999,
            es_inagotable=True,
        )

        # Crear almacén local con un solo silo de comida
        alm = Almacen(nombre=f"Almacén {nombre}")
        alm.agregar_silo(Silo(
            nombre=f"Silo Comida {nombre}",
            tipo_recurso=TipoRecurso.COMIDA,
            capacidad_base=capacidad_silo,
        ))

        return cls(
            nombre=nombre,
            nivel=nivel,
            fuente=fuente,
            coordenada=coordenada,
            almacen=alm,
        )
