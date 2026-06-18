# src/logistica/gps.py
from __future__ import annotations

import heapq
import logging
from typing import TYPE_CHECKING

from src.core.coordenada import Coordenada

if TYPE_CHECKING:
    from src.territorio.mapa import Mapa

logger = logging.getLogger(__name__)


class GPS:
    """
    Calculador de rutas sobre el mapa de puntos.

    Stateless y puro: recibe mapa + origen + destino → devuelve lista de waypoints.
    Usa algoritmo A* con heurística euclídea y costes de terreno.

    Auto-registra puntos como LLANURA si no existen pero están dentro
    de los límites válidos del mapa. Esto garantiza que las rutas siempre
    sean viables sin depender del timing de registro externo.
    """

    # Direcciones de movimiento (8 direcciones: cardinales + diagonales)
    DIRECCIONES: list[tuple[int, int]] = [
        (0, 1), (0, -1), (1, 0), (-1, 0),   # Cardinales
        (1, 1), (1, -1), (-1, 1), (-1, -1),  # Diagonales
    ]

    # src/logistica/gps.py (actualizar método _asegurar_punto)

    @staticmethod
    def _asegurar_punto(mapa: Mapa, coord: Coordenada) -> None:
        """
        Registra un punto como LLANURA si no existe.
        Si ya existe pero NO es transitable, LO REEMPLAZA por una llanura.
        Esto garantiza que las rutas automáticas siempre tengan paso libre.
        """
        from src.territorio.punto import Punto
        from src.territorio.terreno import TipoTerreno

        if coord not in mapa.puntos:
            # Caso 1: No existe → Crear nuevo
            mapa.puntos[coord] = Punto(coordenada=coord)
        else:
            # Caso 2: Existe → Verificar transitabilidad
            punto_existente = mapa.puntos[coord]
            if not punto_existente.es_transitable:
                logger.info(
                    "🔧 GPS: Reemplazando punto no transitable %s (%s) por LLANURA",
                    coord, punto_existente.terreno
                )
                # Reemplazar manteniendo propietario y estructura si existen
                nuevo_punto = Punto(
                    coordenada=coord,
                    terreno=TipoTerreno.LLANURA,
                    propietario=punto_existente.propietario,
                    estructura=punto_existente.estructura,
                    unidades=punto_existente.unidades,
                )
                mapa.puntos[coord] = nuevo_punto

    @staticmethod
    def calcular_ruta(  # noqa: C901
        mapa: Mapa,
        origen: Coordenada,
        destino: Coordenada,
    ) -> list[Coordenada] | None:
        """
        Calcula la ruta óptima entre origen y destino.

        Returns:
            Lista ordenada de Coordenadas desde origen hasta destino (inclusive).
            None si no existe ruta viable.
        """
        if origen == destino:
            return [origen]

        if not mapa.es_coordenada_valida(origen) or not mapa.es_coordenada_valida(destino):
            logger.warning(
                "GPS: Coordenadas fuera de límites. Origen=%s, Destino=%s",
                origen, destino,
            )
            return None

        # ✅ Auto-registrar origen y destino si no existen
        GPS._asegurar_punto(mapa, origen)
        GPS._asegurar_punto(mapa, destino)

        punto_origen = mapa.puntos.get(origen)
        punto_destino = mapa.puntos.get(destino)

        if not punto_origen or not punto_destino:
            logger.warning(
                "GPS: No se pudieron obtener puntos tras auto-registro. "
                "Origen=%s, Destino=%s", origen, destino,
            )
            return None

        if not punto_destino.es_transitable:
            logger.warning("GPS: Destino no transitable: %s", destino)
            return None

        # 🔍 DEBUG TEMPORAL: Verificar estado de puntos en el momento de buscar ruta
        puntos_cercanos = [
            str(c) for c in mapa.puntos.keys()
            if abs(c.x - origen.x) <= 4 and abs(c.y - origen.y) <= 4
        ]
        logger.info(
            "🔍 GPS.calcular_ruta: origen=%s, destino=%s | "
            "origen_en_puntos=%s, destino_en_puntos=%s | "
            "puntos_cercanos_al_origen=%d: %s",
            origen, destino,
            origen in mapa.puntos,
            destino in mapa.puntos,
            len(puntos_cercanos), puntos_cercanos[:10],
        )

        # A* con heap de prioridad
        # Elementos: (f_score, contador, coordenada)
        contador = 0
        open_set: list[tuple[float, int, Coordenada]] = []
        heapq.heappush(open_set, (0.0, contador, origen))

        came_from: dict[Coordenada, Coordenada] = {}
        g_score: dict[Coordenada, float] = {origen: 0.0}
        f_score: dict[Coordenada, float] = {
            origen: GPS._heuristica(origen, destino)
        }

        while open_set:
            _, _, actual = heapq.heappop(open_set)

            if actual == destino:
                return GPS._reconstruir_ruta(came_from, origen, destino)

            for dx, dy in GPS.DIRECCIONES:
                vecino_coord = Coordenada(actual.x + dx, actual.y + dy)

                if not mapa.es_coordenada_valida(vecino_coord):
                    continue

                # ✅ Auto-registrar vecino si no existe pero es coordenada válida
                GPS._asegurar_punto(mapa, vecino_coord)

                vecino_punto = mapa.puntos.get(vecino_coord)
                if vecino_punto is None:
                    continue

                if not vecino_punto.es_transitable:
                    continue

                # Coste = coste_movimiento del terreno destino
                # Diagonal cuesta ×1.41 para evitar zigzags artificiales
                coste_base = vecino_punto.coste_movimiento
                es_diagonal = dx != 0 and dy != 0
                coste_movimiento = coste_base * (1.41 if es_diagonal else 1.0)

                tentative_g = g_score[actual] + coste_movimiento

                if tentative_g < g_score.get(vecino_coord, float('inf')):
                    came_from[vecino_coord] = actual
                    g_score[vecino_coord] = tentative_g
                    f = tentative_g + GPS._heuristica(vecino_coord, destino)
                    f_score[vecino_coord] = f
                    contador += 1
                    heapq.heappush(open_set, (f, contador, vecino_coord))

        logger.warning(
            "GPS: No se encontró ruta entre %s y %s tras explorar %d nodos",
            origen, destino, len(g_score),
        )
        return None  # No se encontró ruta

    @staticmethod
    def _heuristica(a: Coordenada, b: Coordenada) -> float:
        """Heurística euclídea para A*."""
        return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

    @staticmethod
    def _reconstruir_ruta(
        came_from: dict[Coordenada, Coordenada],
        origen: Coordenada,
        destino: Coordenada,
    ) -> list[Coordenada]:
        """Reconstruye la ruta desde destino hasta origen usando came_from."""
        ruta: list[Coordenada] = [destino]
        actual = destino
        while actual != origen:
            actual = came_from[actual]
            ruta.append(actual)
        ruta.reverse()
        return ruta
