# server/estado.py
from src.gestion.controlador_partida import ControladorPartida

# Instancia global del motor de juego (vive en memoria del servidor)
# Al estar en un archivo separado, evitamos importaciones circulares.
game_controller = ControladorPartida()
