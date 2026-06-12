# src/territorio/ciudad.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.core.coordenada import Coordenada
from src.economia.almacen import Almacen  # ← AÑADIR ESTE IMPORT
from src.economia.silo import Silo, TipoRecurso

# Import solo para type hints, evita importación circular
if TYPE_CHECKING:
    from src.config.game_config import GameConfig
    from src.economia.edificios.cuartel import Cuartel
    from src.economia.edificios.palacio import Palacio
    from src.territorio.reino import Reino

def _crear_almacen_ciudad() -> Almacen:
        """
        Crea un almacén urbano con los silos básicos que toda ciudad necesita.
        Esto asegura que las ciudades puedan recibir recursos esenciales sin configuración manual.
        """
        alm = Almacen(nombre="Almacén Central")

        # Silo básico de Comida (esencial para supervivencia y transporte desde granjas)
        alm.agregar_silo(Silo(
            nombre="Silo Comida",
            tipo_recurso=TipoRecurso.COMIDA,
            capacidad_base=500,
        ))

        # ✅ NUEVO: Silo de Madera para recibir de serrerías
        alm.agregar_silo(Silo(
            nombre="Silo Madera",
            tipo_recurso=TipoRecurso.MADERA,
            capacidad_base=500,
        ))

        # Futuro: Añadir aquí silos de Piedra, Hierro, Oro según diseño económico
        # alm.agregar_silo(Silo(...))

        return alm

@dataclass
class Ciudad:
    """
    Representa un asentamiento urbano fijo en el mapa.
    Es el nodo central de la jugabilidad: producción, ejército, diplomacia e investigación.

    La ciudad pertenece a un Reino y contiene edificios urbanos (únicos)
    y edificios productivos (limitados por configuración global).
    """

    # ==========================================
    # PROPIEDADES IDENTITARIAS
    # ==========================================
    nombre: str
    ubicacion: Coordenada
    reino_propietario: Reino  # Referencia al Reino dueño de esta ciudad

    # ==========================================
    # ALMACÉN CENTRAL DE LA CIUDAD
    # ==========================================
    almacen: Almacen = field(default_factory=_crear_almacen_ciudad)

    # ==========================================
    # EDIFICIOS URBANOS (Objetos operativos)
    # ==========================================
    # Los booleans indican si el edificio está construido.
    # Los objetos contienen la lógica (producción, reclutamiento, etc.)
    # Son None hasta que se construye el edificio.
    palacio: Palacio | None = None
    cuartel: Cuartel | None = None

    # ==========================================
    # SEDES DE GOBIERNO (Pueden coexistir)
    # ==========================================
    tiene_palacio: bool = False  # Solo 1 por imperio (capital imperial)
    tiene_castillo: bool = False  # 1 por reino vasallo (o capital imperial)

    # Estado dinámico: ¿Está el Emperador alojado aquí actualmente?
    emperador_alojado: bool = False

    # ==========================================
    # EDIFICIOS URBANOS (Únicos por ciudad)
    # ==========================================
    mercado: bool = False
    taberna: bool = False
    embajada: bool = False

    # ==========================================
    # EDIFICIOS PRODUCTIVOS (Listas limitadas por GameConfig)
    # ==========================================
    granjas: list[Any] = field(default_factory=list)
    serrerias: list[Any] = field(default_factory=list)
    canteras: list[Any] = field(default_factory=list)
    minas_hierro: list[Any] = field(default_factory=list)
    minas_oro: list[Any] = field(default_factory=list)

    # ==========================================
    # VALIDACIONES
    # ==========================================
    def __post_init__(self):
        if not self.nombre.strip():
            raise ValueError("El nombre de la ciudad no puede estar vacío.")
        if self.tiene_palacio and not self.tiene_castillo:
            # El palacio imperial siempre incluye funciones de castillo
            self.tiene_castillo = True

    # ==========================================
    # GESTIÓN DE EDIFICIOS PRODUCTIVOS
    # ==========================================
    # ==========================================
    # GESTIÓN DE EDIFICIOS PRODUCTIVOS
    # ==========================================
    def obtener_edificios_productivos(self) -> list[Any]:
        """
        Devuelve una lista plana con TODOS los edificios productivos de la ciudad.
        Útil para que el ServerTick itere sobre todos sin conocer los tipos internos.
        """
        return (
            self.granjas
            + self.serrerias
            + self.canteras
            + self.minas_hierro
            + self.minas_oro
        )

    def puede_construir(
        self, tipo_edificio: str, config: GameConfig
    ) -> tuple[bool, str]:
        """
        Verifica si se puede construir un nuevo edificio productivo.
        Consulta el límite actualizado desde el singleton de configuración.
        """
        lista_destino = self._get_lista_por_tipo(tipo_edificio)
        if lista_destino is None:
            return False, f"❌ Tipo de edificio desconocido: {tipo_edificio}"

        limite = config.get_max_edificios_productivos(tipo_edificio)
        if len(lista_destino) >= limite:
            return False, f"❌ Límite alcanzado ({limite}) para {tipo_edificio}"

        return True, "✅ Construcción permitida"

    def _get_lista_por_tipo(self, tipo: str) -> list | None:
        """Mapea el string del tipo a la lista correspondiente."""
        mapeo = {
            "granja": self.granjas,
            "serreria": self.serrerias,
            "cantera": self.canteras,
            "mina_hierro": self.minas_hierro,
            "mina_oro": self.minas_oro,
        }
        return mapeo.get(tipo)


    # ==========================================
    # GESTIÓN DEL EMPERADOR
    # ==========================================
    def alojar_emperador(self) -> tuple[bool, str]:
        """Aloja al Emperador en esta ciudad (requiere castillo)."""
        if not self.tiene_castillo:
            return False, "❌ Esta ciudad no tiene castillo para alojar al Emperador."
        if self.emperador_alojado:
            return False, "❌ El Emperador ya está alojado aquí."

        self.emperador_alojado = True
        return True, f"👑 El Emperador se ha alojado en {self.nombre}"

    def despedir_emperador(self) -> None:
        """El Emperador abandona esta ciudad."""
        self.emperador_alojado = False

    # ==========================================
    # CONSULTAS RÁPIDAS
    # ==========================================
    def es_capital_imperial(self) -> bool:
        return self.tiene_palacio

    def es_capital_vasalla(self) -> bool:
        return self.tiene_castillo and not self.tiene_palacio

    def total_edificios_productivos(self) -> int:
        return (
            len(self.granjas)
            + len(self.serrerias)
            + len(self.canteras)
            + len(self.minas_hierro)
            + len(self.minas_oro)
        )

    def __str__(self) -> str:
        tipo = (
            "Capital Imperial"
            if self.tiene_palacio
            else "Capital Vasalla" if self.tiene_castillo else "Villa"
        )
        huesped = " 👑" if self.emperador_alojado else ""
        return f"🏙️ {self.nombre} ({tipo}{huesped}) en {self.ubicacion}"
