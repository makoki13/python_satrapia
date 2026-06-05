# server/websocket/gestor_ws.py

from fastapi import WebSocket


class ConnectionManager:
    """
    Gestiona las conexiones WebSocket activas.
    Agrupa las conexiones por 'partida_id' para hacer broadcasts eficientes.
    """

    def __init__(self):
        # Diccionario: clave = partida_id, valor = lista de WebSockets conectados
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, partida_id: str):
        """
        Registra la conexión en la sala de la partida.
        NOTA: El websocket.accept() ya se hizo en main.py, aquí solo registramos.
        """
        # ❌ ELIMINADO: await websocket.accept()  ← Esta línea causaba el problema
        if partida_id not in self.active_connections:
            self.active_connections[partida_id] = []
        self.active_connections[partida_id].append(websocket)
        print(f"🔌 [WS] Nuevo cliente conectado a la partida {partida_id[:8]}...")

    def disconnect(self, websocket: WebSocket, partida_id: str):
        """Limpia la conexión cuando un jugador se desconecta."""
        if partida_id in self.active_connections:
            if websocket in self.active_connections[partida_id]:
                self.active_connections[partida_id].remove(websocket)
            if not self.active_connections[partida_id]:
                del self.active_connections[partida_id]
        print(f"🔌 [WS] Cliente desconectado de la partida {partida_id[:8]}...")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envía un mensaje privado a un cliente específico."""
        await websocket.send_json(message)

    async def broadcast_to_game(self, partida_id: str, message: dict):
        """
        Envía un mensaje (ej. Resumen de Turno) a TODOS los jugadores
        conectados en una partida específica.
        """
        if partida_id in self.active_connections:
            for connection in self.active_connections[partida_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Si la conexión está rota, la ignoramos
                    pass

# Instancia global que usará FastAPI
manager = ConnectionManager()
