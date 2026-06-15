# src/territorio/entidad.py
"""
Protocolos e interfaces comunes para entidades del juego.
"""

# Protocol define interfaces estructurales (duck typing estático).
# runtime_checkable permite usar isinstance() en runtime con Protocols.
from typing import Protocol, runtime_checkable


@runtime_checkable
class EntidadPolitica(Protocol):
    """
    Interfaz para cualquier entidad que puede poseer territorio:
    reinos, tribus, alianzas, etc.

    Cualquier clase con un atributo `nombre: str` cumple este Protocol
    automáticamente (subtipado estructural).
    """
    nombre: str
