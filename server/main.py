# server/main.py
import json

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from server.api.rutas_admin import router as admin_router
from server.api.rutas_jugador import router as jugador_router
from server.config import settings
from server.estado import game_controller
from server.websocket.gestor_ws import manager  # <-- Importamos el gestor

app = FastAPI(
    title="Satrapia API",
    description="API para el juego de estrategia Satrapia",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin", tags=["Administración"])
app.include_router(jugador_router, prefix="/jugador", tags=["Jugador"])

@app.get("/")
async def root():
    return {
        "mensaje": "🏛️ Bienvenido al servidor de Satrapia",
        "version": "0.1.0",
        "partidas_activas": len(game_controller.partidas_activas)
    }

# ==========================================
# ENDPOINT DE WEBSOCKET (¡La magia en tiempo real!)
# ==========================================
@app.websocket("/ws/{partida_id}/{jugador_nombre}")
async def websocket_endpoint(websocket: WebSocket, partida_id: str, jugador_nombre: str):
    """
    Punto de conexión para los clientes.
    Un jugador se conecta a la sala de su partida.
    """
    await manager.connect(websocket, partida_id)

    # Mensaje de bienvenida al conectarse
    await manager.send_personal_message(
        {"tipo": "bienvenida", "mensaje": f"Conectado a la partida {partida_id} como {jugador_nombre}"},
        websocket
    )

    try:
        while True:
            # El servidor se queda escuchando indefinidamente lo que mande el cliente
            data = await websocket.receive_text()

            # Por ahora, hacemos un simple "eco" o procesamos comandos básicos
            try:
                comando = json.loads(data)
                accion = comando.get("accion")

                if accion == "chat":
                    # Broadcast a todos en la misma partida
                    await manager.broadcast_to_game(partida_id, {
                        "tipo": "chat",
                        "jugador": jugador_nombre,
                        "mensaje": comando.get("mensaje")
                    })
                elif accion == "orden":
                    # Aquí conectaríamos con game_controller.procesar_orden() en el futuro
                    await manager.send_personal_message({
                        "tipo": "ack",
                        "mensaje": f"Orden recibida: {comando.get('tipo_orden')}"
                    }, websocket)

            except json.JSONDecodeError:
                await manager.send_personal_message({"error": "Formato JSON inválido"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, partida_id)
        # Avisar a los demás de que alguien se fue
        await manager.broadcast_to_game(partida_id, {
            "tipo": "evento",
            "mensaje": f"⚠️ {jugador_nombre} se ha desconectado."
        })

if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
