# src/api/dependencias.py
"""
Dependencias globales de la API.
Se inicializan una vez al arrancar el servidor FastAPI.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config.game_config import GameConfig
    from src.gestion.partida import Partida
    from src.investigacion.arbol_investigaciones import ArbolInvestigaciones

# Singletons globales (se asignan en main.py al arrancar)
CONFIG_GLOBAL: GameConfig | None = None
ARBOL_GLOBAL: ArbolInvestigaciones | None = None

# Registro de partidas activas (futuro: Redis/DB)
_partidas_activas: dict[str, Partida] = {}


def obtener_partida_activa(partida_id: str) -> Partida | None:
    return _partidas_activas.get(partida_id)


def registrar_partida(partida: Partida) -> None:
    _partidas_activas[partida.id] = partida


def inicializar_dependencias(config: GameConfig, arbol: ArbolInvestigaciones) -> None:
    """Llamar una vez al arrancar el servidor."""
    global CONFIG_GLOBAL, ARBOL_GLOBAL
    CONFIG_GLOBAL = config
    ARBOL_GLOBAL = arbol
