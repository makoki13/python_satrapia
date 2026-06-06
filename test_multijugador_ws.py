# test_multijugador_ws.py
"""
Script que prueba la comunicación en tiempo real con múltiples jugadores.
Simula una sala de juego donde varios clientes escuchan eventos simultáneamente.
"""
import asyncio
import json

import requests
import websockets

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

# Colores para la terminal (para distinguir jugadores)
COLORS = {
    "cesar": "\033[94m",    # Azul
    "atila": "\033[91m",    # Rojo
    "satrapa": "\033[92m",  # Verde
    "reset": "\033[0m"      # Reset
}

async def cliente_jugador(nombre_personaje: str, partida_id: str):
    """
    Simula un jugador conectado por WebSocket.
    Escucha eventos y los muestra en pantalla con su color asignado.
    """
    color = COLORS.get(nombre_personaje.lower().split()[0], COLORS["reset"])

    print(f"{color}[{nombre_personaje}] Conectando al WebSocket...{COLORS['reset']}")

    async with websockets.connect(WS_URL) as websocket:
        # Enviar información de conexión
        await websocket.send(json.dumps({
            "partida_id": partida_id,
            "jugador_nombre": nombre_personaje
        }))

        # Recibir bienvenida
        bienvenida = await websocket.recv()
        data = json.loads(bienvenida)
        print(f"{color}[{nombre_personaje}] ✅ {data['mensaje']}{COLORS['reset']}")

        # Bucle principal: escuchar eventos indefinidamente
        print(f"{color}[{nombre_personaje}] 🎧 Escuchando eventos en tiempo real...{COLORS['reset']}")

        try:
            while True:
                mensaje = await websocket.recv()
                data = json.loads(mensaje)

                tipo = data.get("tipo", "desconocido")

                if tipo == "turno_avanzado":
                    resumen = data.get("resumen", {})
                    turno = resumen.get("turno", "?")
                    eventos = resumen.get("eventos", [])

                    print(f"\n{color}[{nombre_personaje}] ⏰ ¡TURNO {turno} AVANZADO!{COLORS['reset']}")
                    for evento in eventos:
                        print(f"{color}   • {evento}{COLORS['reset']}")
                    print(f"{color}   👥 Jugadores activos: {resumen.get('jugadores_activos', '?')}{COLORS['reset']}")

                elif tipo == "chat":
                    jugador = data.get("jugador", "?")
                    mensaje_chat = data.get("mensaje", "")
                    print(f"\n{color}[{nombre_personaje}] 💬 {jugador}: {mensaje_chat}{COLORS['reset']}")

                elif tipo == "evento":
                    mensaje_evento = data.get("mensaje", "")
                    print(f"\n{color}[{nombre_personaje}] ℹ️ {mensaje_evento}{COLORS['reset']}")

                elif tipo == "bienvenida":
                    pass  # Ya lo mostramos arriba

                else:
                    print(f"{color}[{nombre_personaje}] 📨 Evento desconocido: {data}{COLORS['reset']}")

        except websockets.exceptions.ConnectionClosed:
            print(f"{color}[{nombre_personaje}] 🔌 Conexión cerrada.{COLORS['reset']}")
        except Exception as e:
            print(f"{color}[{nombre_personaje}] ❌ Error: {e}{COLORS['reset']}")


async def flujo_completo():
    """Orquesta todo el flujo: crear partida, unir jugadores, conectar WebSockets."""
    print("🎮 === PRUEBA MULTIJUGADOR EN TIEMPO REAL ===\n")

    # 1. Crear partida
    print("1️⃣ Creando partida...")
    response = requests.post(f"{BASE_URL}/admin/partidas/crear", json={
        "nombre": "Batalla Multijugador",
        "modo_desarrollo": True
    })
    partida_data = response.json()
    partida_id = partida_data["partida_id"]
    print(f"   ✅ Partida creada: {partida_data['mensaje']}")
    print(f"   🆔 ID: {partida_id}\n")

    # 2. Unir jugadores
    print("2️⃣ Uniendo jugadores...")
    jugadores_info = [
        ("cesar", "César Augusto"),
        ("atila", "Atila el Huno"),
        ("satrapa", "Darío I")
    ]

    for username, nombre_personaje in jugadores_info:
        response = requests.post(f"{BASE_URL}/jugador/unirse", json={
            "partida_id": partida_id,
            "username": username,
            "email": f"{username}@satrapia.com",
            "password": "Password123!",
            "nombre_personaje": nombre_personaje
        })
        data = response.json()
        if data.get("exito"):
            print(f"   ✅ {nombre_personaje} unido")
        else:
            print(f"   ❌ Error al unir {nombre_personaje}: {data.get('detail')}")

    print("\n3️⃣ Conectando clientes WebSocket...")
    print("   (Los clientes se conectarán y esperarán eventos)\n")

    # 3. Conectar los 3 clientes WebSocket simultáneamente
    tasks = []
    for _, nombre_personaje in jugadores_info:
        task = asyncio.create_task(cliente_jugador(nombre_personaje, partida_id))
        tasks.append(task)

    # Esperar un momento para que todos se conecten
    await asyncio.sleep(2)

    # 4. Iniciar la partida (esto disparará el primer evento)
    print("\n4️⃣ Iniciando partida desde Admin...")
    print("   (Observa cómo TODOS los clientes reciben el evento simultáneamente)\n")

    response = requests.post(f"{BASE_URL}/admin/partidas/{partida_id}/iniciar")
    data = response.json()

    if data.get("exito"):
        print(f"   ✅ {data['mensaje']}\n")
    else:
        print(f"   ❌ Error al iniciar: {data.get('detail')}\n")

    # 5. Esperar a ver varios turnos avanzando automáticamente
    print("5️⃣ Observando avances de turno automáticos...")
    print("   (El Server Tick avanza cada 10 segundos)\n")

    # Esperar 35 segundos para ver ~3 turnos
    await asyncio.sleep(35)

    # Cancelar las tareas de los clientes
    for task in tasks:
        task.cancel()

    print("\n🏁 === PRUEBA COMPLETADA ===")
    print("\n💡 Lo que acabas de ver:")
    print("   • Todos los clientes recibieron el evento de inicio AL MISMO TIEMPO")
    print("   • Cada 10 segundos, todos recibieron el avance de turno SIN preguntar")
    print("   • Esto es la base de un juego multijugador en tiempo real")


if __name__ == "__main__":
    print("Asegúrate de que el servidor está corriendo (python -m server.main)")
    print("Y que TURN_DURATION_SECONDS está configurado a 10 en config.py\n")
    asyncio.run(flujo_completo())
