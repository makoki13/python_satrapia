# test_cliente_completo.py
"""
Script de prueba usando websockets (la librería oficial compatible con FastAPI)
"""
import asyncio
import json

import requests
import websockets

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

# test_cliente_completo.py (solo la parte de conexión)
async def flujo_completo_jugador():
    print("🎮 === INICIANDO FLUJO DE JUGADOR ===\n")

    # 1. Crear partida
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

    # test_cliente_completo.py (añadir después de unir a Marco Agripa)

    # 2.5. Unir un segundo jugador
    print("2.5️⃣ Uniendo segundo jugador...")
    response2 = requests.post(f"{BASE_URL}/jugador/unirse", json={
        "partida_id": partida_id,
        "username": "cleopatra",
        "email": "cleo@egipto.com",
        "password": "PasswordSegura123!",
        "nombre_personaje": "Cleopatra"
    })
    union_data2 = response2.json()
    print(f"   ✅ {union_data2['mensaje']}")
    print(f"   👤 Personaje: {union_data2['jugador_nombre']}\n")

    # 3. Conectar al WebSocket
    print("3️⃣ Conectando al WebSocket...")

    async with websockets.connect(WS_URL) as websocket:
        # ¡IMPORTANTE! Enviar información INMEDIATAMENTE después de conectar
        print("   📤 Enviando información de conexión...")
        await websocket.send(json.dumps({
            "partida_id": partida_id,
            "jugador_nombre": union_data['jugador_nombre']
        }))

        print("   ✅ WebSocket conectado, esperando bienvenida...")

        # Recibir bienvenida
        bienvenida = await websocket.recv()
        print(f"   📨 Servidor: {bienvenida}\n")

        # 4. Enviar mensaje de chat
        print("4️⃣ Enviando mensaje de chat...")
        await websocket.send(json.dumps({
            "accion": "chat",
            "mensaje": "¡Roma dominará el Mediterráneo!"
        }))

        chat_recibido = await websocket.recv()
        print(f"   💬 Chat broadcast: {chat_recibido}\n")

        # 5. Enviar orden de juego
        print("5️⃣ Dando una orden al motor...")
        await websocket.send(json.dumps({
            "accion": "orden",
            "tipo_orden": "mover_faccion",
            "destino": {"x": 50, "y": 50}
        }))

        respuesta = await websocket.recv()
        print(f"   ⚔️ Respuesta: {respuesta}\n")

        print("6️⃣ Esperando 10 segundos para capturar eventos...")
        try:
            for _ in range(10):
                await asyncio.sleep(1)
                try:
                    evento = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    print(f"   🎮 Evento: {evento}")
                except asyncio.TimeoutError:
                    pass
        except KeyboardInterrupt:
            pass

    print("\n🏁 === FLUJO COMPLETADO ===")

if __name__ == "__main__":
    print("Asegúrate de que el servidor está corriendo (python -m server.main)\n")
    asyncio.run(flujo_completo_jugador())
