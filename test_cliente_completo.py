# test_cliente_completo.py
"""
Script de prueba que simula el flujo completo de un jugador:
1. Se une a una partida vía HTTP
2. Se conecta al WebSocket
3. Escucha eventos en tiempo real
4. Envía una orden de juego
"""
import asyncio
import json

import requests
import websockets

# Configuración
BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

async def flujo_completo_jugador():
    print("🎮 === INICIANDO FLUJO DE JUGADOR ===\n")

    # 1. Crear partida (simulando al admin)
    print("1️⃣ Creando partida como Admin...")
    response = requests.post(f"{BASE_URL}/admin/partidas/crear", json={
        "nombre": "Batalla de Actium",
        "modo_desarrollo": True
    })
    partida_data = response.json()
    partida_id = partida_data["partida_id"]
    print(f"   ✅ Partida creada: {partida_data['mensaje']}")
    print(f"   🆔 ID: {partida_id}\n")

    # 2. Unirse como jugador
    print("2️⃣ Uniéndose a la partida como jugador...")
    response = requests.post(f"{BASE_URL}/jugador/unirse", json={
        "partida_id": partida_id,
        "username": "marco_agripa",
        "email": "agripa@roma.com",
        "password": "PasswordSegura123!",
        "nombre_personaje": "Marco Agripa"
    })
    union_data = response.json()
    print(f"   ✅ {union_data['mensaje']}")
    print(f"   👤 Personaje: {union_data['jugador_nombre']}\n")

    # 3. Conectar al WebSocket
    print("3️⃣ Conectando al WebSocket...")
    ws_uri = f"{WS_URL}/{partida_id}/{union_data['jugador_nombre']}"

    async with websockets.connect(ws_uri) as websocket:
        # Recibir bienvenida
        bienvenida = await websocket.recv()
        print(f"   📨 Servidor: {bienvenida}\n")

        # 4. Enviar un mensaje de chat
        print("4️⃣ Enviando mensaje de chat a la sala...")
        await websocket.send(json.dumps({
            "accion": "chat",
            "mensaje": "¡Roma dominará el Mediterráneo!"
        }))

        chat_recibido = await websocket.recv()
        print(f"   💬 Chat broadcast: {chat_recibido}\n")

        # 5. Enviar una orden de juego
        print("5️⃣ Dando una orden al motor del juego...")
        await websocket.send(json.dumps({
            "accion": "orden",
            "tipo_orden": "mover_faccion",
            "destino": {"x": 50, "y": 50}
        }))

        respuesta = await websocket.recv()
        print(f"   ⚔️ Respuesta: {respuesta}\n")

        # 6. Forzar inicio de partida (vía HTTP) y ver evento
        print("6️⃣ Forzando inicio de partida desde admin...")
        print("   (Abre otra terminal o Swagger y haz POST /admin/partidas/{id}/iniciar)")
        print("   Esperando 10 segundos para capturar evento...\n")

        try:
            evento = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"   🎮 Evento recibido: {evento}")
        except asyncio.TimeoutError:
            print("   ⏱️ No llegó evento en 10 segundos (normal si no forzaste el inicio)")

    print("\n🏁 === FLUJO COMPLETADO ===")

if __name__ == "__main__":
    print("Asegúrate de que el servidor está corriendo (python -m server.main)\n")
    asyncio.run(flujo_completo_jugador())
