# server/main.py
import asyncio
import json
import logging

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from server.api.rutas_admin import router as admin_router
from server.api.rutas_jugador import router as jugador_router
from server.config import settings
from server.estado import game_controller
from server.websocket.gestor_ws import manager

logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logging.getLogger("watchfiles.watcher").setLevel(logging.WARNING)
# logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Opcional: silencia requests HTTP

app = FastAPI(title="Satrapia API")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Satrapia API",
    description="API para el juego de estrategia Satrapia",
    version="0.1.0"
)

# Configurar CORS (permite que el cliente se conecte desde otro origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Cambiado a False para compatibilidad con WebSockets
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(admin_router, prefix="/admin", tags=["Administración"])
app.include_router(jugador_router, prefix="/jugador", tags=["Jugador"])

@app.get("/")
async def root():
    """Endpoint de verificación de que el servidor está vivo."""
    return {
        "mensaje": "🏛️ Bienvenido al servidor de Satrapia",
        "version": "0.1.0",
        "partidas_activas": len(game_controller.partidas_activas)
    }

@app.get("/health")
async def health_check():
    """Endpoint para monitoreo de salud del servidor."""
    return {"status": "healthy", "partidas": len(game_controller.partidas_activas)}

# ==========================================
# ENDPOINT DE WEBSOCKET (Ruta simplificada)
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):  # noqa: C901
    """
    Punto de conexión para los clientes.
    El cliente debe enviar partida_id y jugador_nombre como primer mensaje.
    """
    logger.info("🔌 Nueva conexión WebSocket recibida")

    partida_id = None
    jugador_nombre = None

    try:
        await websocket.accept()
        logger.info("✅ Conexión WebSocket aceptada")

        # Recibir el primer mensaje con información de conexión
        logger.info("⏳ Esperando primer mensaje del cliente...")
        data = await websocket.receive_text()
        logger.info(f"📨 Mensaje recibido: {data}")

        try:
            info = json.loads(data)
            partida_id = info.get("partida_id")
            jugador_nombre = info.get("jugador_nombre")
        except json.JSONDecodeError:
            logger.error("❌ Primer mensaje no es JSON válido")
            await websocket.send_json({"error": "Primer mensaje debe ser JSON con partida_id y jugador_nombre"})
            await websocket.close()
            return

        logger.info(f"🎮 Partida ID: {partida_id}, Jugador: {jugador_nombre}")

        # Validar que tenemos los datos necesarios
        if not partida_id or not jugador_nombre:
            logger.error("❌ Faltan partida_id o jugador_nombre")
            await websocket.send_json({"error": "Faltan partida_id o jugador_nombre"})
            await websocket.close()
            return

        # Validar que la partida existe
        if partida_id not in game_controller.partidas_activas:
            logger.error(f"❌ Partida {partida_id} no encontrada")
            logger.info(f"📋 Partidas activas: {list(game_controller.partidas_activas.keys())}")
            await websocket.send_json({"error": "Partida no encontrada"})
            await websocket.close()
            return

        # Registrar la conexión en el gestor
        logger.info("✅ Partida válida, registrando conexión...")
        await manager.connect(websocket, partida_id)

        # Enviar mensaje de bienvenida
        bienvenida = {
            "tipo": "bienvenida",
            "mensaje": f"Conectado a la partida {partida_id} como {jugador_nombre}"
        }
        logger.info(f"📤 Enviando bienvenida: {bienvenida}")
        await websocket.send_json(bienvenida)

        # Bucle principal de comunicación
        logger.info("🔄 Entrando en bucle de mensajes...")
        while True:
            data = await websocket.receive_text()
            logger.info(f"📨 Mensaje recibido: {data}")

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
                    logger.info(f"💬 Chat broadcast enviado por {jugador_nombre}")

                elif accion == "orden":
                    # Confirmación de orden recibida
                    await websocket.send_json({
                        "tipo": "ack",
                        "mensaje": f"Orden recibida: {comando.get('tipo_orden')}"
                    })
                    logger.info(f"⚔️ Orden procesada: {comando.get('tipo_orden')}")

                else:
                    logger.warning(f"⚠️ Acción desconocida: {accion}")
                    await websocket.send_json({"error": f"Acción desconocida: {accion}"})

            except json.JSONDecodeError:
                logger.error("❌ JSON inválido recibido")
                await websocket.send_json({"error": "Formato JSON inválido"})

    except WebSocketDisconnect:
        logger.info(f"🔌 Cliente desconectado: {jugador_nombre}")
        if partida_id:
            manager.disconnect(websocket, partida_id)
            # Avisar a los demás de que alguien se fue
            await manager.broadcast_to_game(partida_id, {
                "tipo": "evento",
                "mensaje": f"⚠️ {jugador_nombre} se ha desconectado."
            })
    except Exception as e:
        logger.error(f"❌ Error inesperado en WebSocket: {e}")
        import traceback
        logger.error(traceback.format_exc())
        try:
            await websocket.close()
        except:  # noqa: E722
            pass

# server/main.py (añadir al final, antes del if __name__ == "__main__":)

async def server_tick():
    """
    Bucle principal del servidor.
    Cada TURN_DURATION_SECONDS, avanza los turnos de todas las partidas activas.
    """
    logger.info(f"⏰ Server Tick iniciado. Intervalo: {settings.TURN_DURATION_SECONDS}s")

    while True:
        await asyncio.sleep(settings.TURN_DURATION_SECONDS)

        # Recorrer todas las partidas activas
        for partida_id, partida in list(game_controller.partidas_activas.items()):
            from src.gestion.partida import EstadoPartida

            # Solo procesar partidas en curso
            if partida.estado == EstadoPartida.EN_CURSO:
                logger.info(f"⏳ Avanzando turno de partida {partida.nombre}...")

                # Avanzar el turno en el motor
                exito, resumen = await game_controller.avanzar_turno(partida_id)

                if exito:
                    # Enviar el resumen a todos los jugadores conectados
                    await manager.broadcast_to_game(partida_id, {
                        "tipo": "turno_avanzado",
                        "resumen": resumen
                    })
                    logger.info(f"✅ Turno {resumen['turno']} completado para {partida.nombre}")

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando el servidor arranca."""
    logger.info("🚀 Servidor Satrapia iniciando...")
    # Iniciar el reloj del servidor en segundo plano
    asyncio.create_task(server_tick())
    logger.info("⏰ Reloj del servidor activado")

# Punto de entrada para ejecución directa
if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor Satrapia...")
    logger.info(f"📡 Host: {settings.HOST}:{settings.PORT}")

    uvicorn.run(
        "server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Recarga automática cuando cambias código
        log_level="info"
    )
