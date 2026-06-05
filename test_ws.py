# test_ws.py
import asyncio
import json

import websockets


async def probar_conexion():
    # Nos conectamos a la ruta que definimos en main.py
    uri = "ws://127.0.0.1:8000/ws/partida-123/Ciro_El_Grande"

    async with websockets.connect(uri) as websocket:
        # 1. Recibir el mensaje de bienvenida
        bienvenida = await websocket.recv()
        print(f"Servidor dice: {bienvenida}")

        # 2. Enviar un mensaje de chat
        await websocket.send(json.dumps({
            "accion": "chat",
            "mensaje": "¡Hola a todos, preparad vuestros tributos!"
        }))

        # 3. Recibir nuestro propio mensaje (broadcast)
        chat_recibido = await websocket.recv()
        print(f"Chat recibido: {chat_recibido}")

        # 4. Enviar una orden de juego
        await websocket.send(json.dumps({
            "accion": "orden",
            "tipo_orden": "mover_faccion",
            "destino": {"x": 50, "y": 50}
        }))

        ack = await websocket.recv()
        print(f"Respuesta del servidor: {ack}")

if __name__ == "__main__":
    print("Iniciando cliente WebSocket de pruebas...")
    asyncio.run(probar_conexion())
