# server/estado.py
import uuid
from dataclasses import dataclass, field

from src.gestion.controlador_partida import ControladorPartida

# Instancia global del motor de juego (vive en memoria del servidor)
# Al estar en un archivo separado, evitamos importaciones circulares.
game_controller = ControladorPartida()

# server/estado.py

@dataclass
class Usuario:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str = ""

# Almacén en memoria (sin persistencia)
usuarios_registrados: dict[str, Usuario] = {}
