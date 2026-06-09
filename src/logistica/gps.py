# src/logistica/gps.py
from __future__ import annotations

import heapq
from typing import TYPE_CHECKING

from src.core.coordenada import Coordenada

if TYPE_CHECKING:
    from src.territorio.mapa import Mapa


class GPS:
    """
    Calculador de rutas sobre el mapa de puntos.

    Stateless y puro: recibe mapa + origen + destino → devuelve lista de waypoints.
    Usa algoritmo A* con heurística euclídea y costes de terreno.
    """

    # Direcciones de movimiento (8 direcciones: cardinales + diagonales)
    DIRECCIONES: list[tuple[int, int]] = [
        (0, 1), (0, -1), (1, 0), (-1, 0),   # Cardinales
        (1, 1), (1, -1), (-1, 1), (-1, -1),  # Diagonales
    ]

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
            return None

        punto_origen = mapa.puntos.get(origen)
        punto_destino = mapa.puntos.get(destino)

        if not punto_origen or not punto_destino:
            return None

        if not punto_destino.es_transitable():
            return None

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

                vecino_punto = mapa.puntos.get(vecino_coord)
                if not vecino_punto or not vecino_punto.es_transitable():
                    continue

                # Coste = coste_movimiento del terreno destino
                # Diagonal cuesta ×1.41 para evitar zigzags artificiales
                coste_base = vecino_punto.get_coste_movimiento()
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
